from PIL import Image

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed

from debates.models import Debate
from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
from toponomikon.models import Location
from users.models import User, Profile

COLORS = (
    ('#000000', 'czarny'),
    ('#C70039', 'czerwony'),
    ('#800080', 'fioletowy'),
    ('#000080', 'granatowy'),
    ('#2e86c1', 'niebieski'),
    ('#FFC300', 'pomarańczowy'),
    ('#808080', 'szary'),
    ('#229954', 'zielony'),
)


# ------ Chapter and GameSession models ------

class Chapter(models.Model):
    chapter_no = models.IntegerField(null=True)
    title = models.CharField(max_length=200)
    image = models.ImageField(blank=True, null=True, upload_to='site_features_pics')

    class Meta:
        ordering = ['chapter_no']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)


class GameSession(models.Model):
    game_no = models.IntegerField(null=True)
    title = models.CharField(max_length=200)
    chapter = models.ForeignKey(Chapter, related_name='game_sessions', on_delete=models.PROTECT, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['game_no']

    def __str__(self):
        return f'{self.game_no} - {self.title}'


# ------ ChronicleEvent model and connected models ------


class ChronicleEvent(models.Model):
    """
    This model is not connected with TimelineEvent model. There is not 121 or M2M relationships between them.
    TimelineEvent model serves to create events in history view (chronology).
    EventDescription serves to create events in the full history text of the game.
    Lack or correspondence between the two is intentional for flexibility.
    """
    # default=35 for events outside of sessions (instance of 'GameSession' for background events has id=35):
    game = models.ForeignKey(GameSession,
                             related_name='chronicle_events',
                             on_delete=models.PROTECT,
                             default=35)
    event_no_in_game = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    description = models.TextField(max_length=10000)
    participants = models.ManyToManyField(Profile,
                                          related_name='chronicle_events_participated',
                                          limit_choices_to=
                                          Q(status='active_player') |
                                          Q(status='inactive_player') |
                                          Q(status='dead_player'),
                                          blank=True)
    informed = models.ManyToManyField(Profile,
                                      related_name='chronicle_events_informed',
                                      limit_choices_to=
                                      Q(status='active_player') |
                                      Q(status='inactive_player') |
                                      Q(status='dead_player'),
                                      blank=True)
    pictures = models.ManyToManyField(to=Picture, related_name='chronicle_events_pics', blank=True)
    debate = models.OneToOneField(Debate,
                                  related_name='chronicle_event',
                                  on_delete=models.PROTECT,
                                  blank=True,
                                  null=True)
    
    class Meta:
        ordering = ['game', 'event_no_in_game']
        
    def __str__(self):
        return f'{self.description[0:100]}{"..." if len(self.description[::]) > 100 else ""}'
    
    def informable(self):
        participants = self.participants.all()
        informed = self.informed.all()
        excluded = (participants | informed).distinct()
        informable = Profile.objects.filter(
            status='active_player'
        ).exclude(id__in=excluded)
        return informable

    def short_description(self):
        return f'{self.description[:100]}...{self.description[-100:] if len(str(self.description)) > 200 else self.description}'


# class ChronicleEventNote(models.Model):
#     author = models.ForeignKey(User, related_name='chronicle_events_notes', on_delete=models.CASCADE)
#     text = models.TextField(max_length=4000, blank=True, null=True)
#     event = models.ForeignKey(ChronicleEvent, related_name='notes', on_delete=models.PROTECT)
#     color = models.CharField(max_length=20, choices=COLORS, default='#C70039')
#
#     def __str__(self):
#         return f'{self.text[0:50]}...'


# ------ TimelineEvent model and connected models ------


SEASONS = (
    ('1', 'Wiosna'),
    ('2', 'Lato'),
    ('3', 'Jesień'),
    ('4', 'Zima')
)


class Thread(models.Model):
    name = models.CharField(max_length=200)
    is_ended = models.BooleanField(default=False)
    sorting_name = models.CharField(max_length=250, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(Thread, self).save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']


class TimelineEvent(models.Model):
    # default=35 for events outside of sessions (instance of 'GameSession' for background events has id=35):
    game = models.ForeignKey(GameSession, related_name='timeline_events', on_delete=models.PROTECT, default=35)
    # year has to be > 0, for url patterns (they accept positive nums only):
    year = models.IntegerField(validators=[MinValueValidator(1)])
    season = models.CharField(max_length=10, choices=SEASONS)
    day_start = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)])
    day_end = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(90)])
    threads = models.ManyToManyField(Thread, related_name='timeline_events', blank=True)
    description = models.TextField(max_length=4000)
    participants = models.ManyToManyField(Profile,
                                          related_name='timeline_events_participated',
                                          limit_choices_to=
                                          Q(status='active_player') |
                                          Q(status='inactive_player') |
                                          Q(status='dead_player'),
                                          blank=True)
    informed = models.ManyToManyField(Profile,
                                      related_name='timeline_events_informed',
                                      limit_choices_to=
                                      Q(status='active_player') |
                                      Q(status='inactive_player'),
                                      blank=True)
    # general_locations = models.ManyToManyField(GeneralLocation, related_name='timeline_events')
    # specific_locations = models.ManyToManyField(SpecificLocation, related_name='timeline_events')
    gen_locations = models.ManyToManyField(Location, related_name='timeline_events_in_gen')
    spec_locations = models.ManyToManyField(Location, related_name='timeline_events_in_spec')
    # locations = models.ManyToManyField(Location, related_name='timeline_events')
    
    class Meta:
        # ordering via 'description' before 'game' to leave flexibility for events with later 'id'-s
        ordering = ['game', 'year', 'season', 'day_start', 'day_end', 'description']
        indexes = [
            models.Index(fields=['year', 'season', 'day_start', 'day_end', 'description', 'game']),
            models.Index(fields=['year', ]),
            models.Index(fields=['season', ]),
            models.Index(fields=['day_start', ]),
            models.Index(fields=['day_end', ]),
            models.Index(fields=['description', ]),
            models.Index(fields=['game', ]),
        ]

    def __str__(self):
        return f'{self.description[0:100]}{"..." if len(self.description[::]) > 100 else ""}'

    def days(self):
        return f'{self.day_start}-{self.day_end}' if self.day_end else self.day_start

    def date(self):
        if self.season == 'spring':
            season = 'Wiosny'
        elif self.season == 'summer':
            season = 'Lata'
        elif self.season == 'autumn':
            season = 'Jesieni'
        else:
            season = 'Zimy'
        return f'{self.days()}. dnia {season} {self.year}. ' \
               f'roku Archonatu Nemetha Samatiana'
    
    def informable(self):
        participants = self.participants.all()
        informed = self.informed.all()
        excluded = (participants | informed).distinct()
        informable = Profile.objects.filter(
            status='active_player'
        ).exclude(id__in=excluded)
        return informable
    
    def short_description(self):
        return self.__str__()


# class TimelineEventNote(models.Model):
#     author = models.ForeignKey(User, related_name='timeline_events_notes', on_delete=models.CASCADE)
#     text = models.TextField(max_length=4000, blank=True, null=True)
#     event = models.ForeignKey(TimelineEvent, related_name='notes', on_delete=models.PROTECT)
#     color = models.CharField(max_length=20, choices=COLORS, default='#C70039')
#
#     def __str__(self):
#         return f'{self.text[0:50]}...'


def update_known_spec_locations(sender, instance, **kwargs):
    """Whenever a profile becomes 'participant' or 'informed' of an event in
    specific location add this location to profile's 'known_directly'
    (if participant) or 'known_indirectly' (if informed).
    """
    participants = instance.participants.all()
    informed = instance.informed.all()
    spec_locations = instance.spec_locations.all()
    for spec_location in spec_locations:
        spec_location.known_directly.add(*participants)
        spec_location.known_indirectly.add(*informed)


post_save.connect(update_known_spec_locations, sender=TimelineEvent)

# Run signal by each change of 'participants', 'informed' or 'spec_locations':
m2m_changed.connect(update_known_spec_locations,
                    sender=TimelineEvent.participants.through)
m2m_changed.connect(update_known_spec_locations,
                    sender=TimelineEvent.informed.through)
m2m_changed.connect(update_known_spec_locations,
                    sender=TimelineEvent.spec_locations.through)

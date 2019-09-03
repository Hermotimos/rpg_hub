from django.db import models
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator
from PIL import Image
from users.models import User, Profile
from imaginarion.models import Picture
from debates.models import Debate


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
        super().save()
        if self.image:
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

    def __str__(self):
        return f'{self.game_no} - {self.title}'

    class Meta:
        ordering = ['game_no']


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
                                          Q(character_status='active_player') |
                                          Q(character_status='inactive_player') |
                                          Q(character_status='dead_player'),
                                          blank=True)
    informed = models.ManyToManyField(Profile,
                                      related_name='chronicle_events_informed',
                                      limit_choices_to=
                                      Q(character_status='active_player') |
                                      Q(character_status='inactive_player') |
                                      Q(character_status='dead_player'),
                                      blank=True)
    pictures = models.ManyToManyField(Picture, related_name='chronicle_events_pics', blank=True)
    debate = models.OneToOneField(Debate,
                                  related_name='chronicle_event',
                                  on_delete=models.PROTECT,
                                  blank=True,
                                  null=True)

    def __str__(self):
        return f'{self.description[0:100]}...'

    def short_description(self):
        return f'{self.description[:100]}...{self.description[-100:] if len(str(self.description)) > 200 else self.description}'

    class Meta:
        ordering = ['game', 'event_no_in_game']


class ChronicleEventNote(models.Model):
    author = models.ForeignKey(User, related_name='chronicle_events_notes', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000, blank=True, null=True)
    event = models.ForeignKey(ChronicleEvent, related_name='notes', on_delete=models.PROTECT)
    color = models.CharField(max_length=20, choices=COLORS, default='#C70039')

    def __str__(self):
        return f'{self.text[0:50]}...'


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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class GeneralLocation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class SpecificLocation(models.Model):
    name = models.CharField(max_length=100)
    general_location = models.ForeignKey(GeneralLocation, related_name='specific_locations', on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


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
                                          Q(character_status='active_player') |
                                          Q(character_status='inactive_player') |
                                          Q(character_status='dead_player'),
                                          blank=True)
    informed = models.ManyToManyField(Profile,
                                      related_name='timeline_events_informed',
                                      limit_choices_to=
                                      Q(character_status='active_player') |
                                      Q(character_status='inactive_player'),
                                      blank=True)
    general_location = models.ForeignKey(GeneralLocation, on_delete=models.DO_NOTHING)
    specific_locations = models.ManyToManyField(SpecificLocation, related_name='timeline_events')

    def __str__(self):
        return f'{self.description[0:100]}{"..." if len(self.description[::]) > 100 else ""}'

    def short_description(self):
        return self.__str__()

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
        return f'{self.days()}. dnia {season} {self.year}. roku Archonatu Nemetha Samatiana'

    class Meta:
        # ordering via 'description' before 'game' to leave flexibility for events with later 'id'-s
        ordering = ['year', 'season', 'day_start', 'day_end', 'description', 'game']

    # Steps to migrate these models:
    # 1) delete migration files, delete tables in db, DELETE FROM django_migrations WHERE app="history";
    # 2) comment out all other models than TimelineEvent
    # 1) migrate Events without any M2M fields or ForeignKeys.
    # 2) uncomment other fields and classes and migrate.


class TimelineEventNote(models.Model):
    author = models.ForeignKey(User, related_name='timeline_events_notes', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000, blank=True, null=True)
    event = models.ForeignKey(TimelineEvent, related_name='notes', on_delete=models.PROTECT)
    color = models.CharField(max_length=20, choices=COLORS, default='#C70039')

    def __str__(self):
        return f'{self.text[0:50]}...'

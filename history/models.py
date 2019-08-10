from django.db import models
from django.db.models import Q
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import User, Profile
from imaginarion.models import Picture


# ------ GameSession model ------


class GameSession(models.Model):
    game_no = models.IntegerField(null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.game_no} - {self.title}'

    class Meta:
        ordering = ['game_no']


# ------ TimelineEvent model and connected models ------


SEASONS = (
    ('1', 'Wiosna'),
    ('2', 'Lato'),
    ('3', 'Jesień'),
    ('4', 'Zima')
)
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


class Thread(models.Model):
    name = models.CharField(max_length=200)

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
    # default=0 for events outside of sessions (background events):
    game_no = models.ForeignKey(GameSession, related_name='events', on_delete=models.PROTECT, default=0)
    # year has to be > 0, for url patterns (they accept positive nums only):
    year = models.IntegerField(validators=[MinValueValidator(1)])
    season = models.CharField(max_length=10, choices=SEASONS)
    day_start = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)])
    day_end = models.PositiveSmallIntegerField(blank=True, null=True,
                                               validators=[MinValueValidator(1), MaxValueValidator(90)])
    threads = models.ManyToManyField(Thread, related_name='events', blank=True)
    description = models.TextField(max_length=4000)
    participants = models.ManyToManyField(Profile,
                                          related_name='events_participated',
                                          limit_choices_to=
                                          Q(character_status='active_player') |
                                          Q(character_status='inactive_player') |
                                          Q(character_status='dead_player'),
                                          blank=True)
    informed = models.ManyToManyField(Profile,
                                      related_name='events_informed',
                                      limit_choices_to=
                                      Q(character_status='active_player') |
                                      Q(character_status='inactive_player'),
                                      blank=True)
    general_location = models.ForeignKey(GeneralLocation, null=True, on_delete=models.SET_NULL)
    specific_locations = models.ManyToManyField(SpecificLocation, related_name='events')

    def __str__(self):
        return f'{self.description[0:100]}...'

    def short_description(self):
        return self.__str__()

    def days(self):
        if self.day_end:
            return f'{self.day_start}-{self.day_end}'
        else:
            return f'{self.day_start}'

    def date(self):
        days = f'{self.day_start}-{self.day_end}' if self.day_end else self.day_start
        if self.season == 'spring':
            season = 'Wiosny'
        elif self.season == 'summer':
            season = 'Lata'
        elif self.season == 'autumn':
            season = 'Jesieni'
        else:
            season = 'Zimy'
        return f'{days}. dzień {season} {self.year}. roku Archonatu Nemetha Samatiana'

    class Meta:
        # ordering via 'description' before 'game_no' to leave flexibility for events with later 'id'-s
        ordering = ['year', 'season', 'day_start', 'day_end', 'description', 'game_no']

    # Steps to migrate these models:
    # 1) delete migration files, delete tables in db, DELETE FROM django_migrations WHERE app="history";
    # 2) comment out all other models than TimelineEvent
    # 1) migrate Events without any M2M fields or ForeignKeys.
    # 2) uncomment other fields and classes and migrate.


class TimelineEventNote(models.Model):
    author = models.ForeignKey(User, related_name='events_notes', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000, blank=True, null=True)
    event = models.ForeignKey(TimelineEvent, related_name='notes', on_delete=models.PROTECT)
    color = models.CharField(max_length=20, choices=COLORS, default='#C70039')

    def __str__(self):
        return f'{self.text[0:50]}...'


# ------ ChronicleEvent model and connected models ------


class ChronicleEvent(models.Model):
    """
    This model is not connected with TimelineEvent model. There is not 121 or M2M relationships between them.
    TimelineEvent model serves to create events in history view (chronology).
    EventDescription serves to create events in the full history text of the game.
    Lack or correspondence between the two is intentional for flexibility.
    """
    # default=0 for events outside of sessions (background events):
    game_no = models.ForeignKey(GameSession,
                                related_name='described_events',
                                on_delete=models.PROTECT,
                                default=0)
    event_no_in_game = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    description = models.TextField(max_length=10000)
    participants = models.ManyToManyField(Profile,
                                          related_name='described_events_participated',
                                          limit_choices_to=
                                          Q(character_status='active_player') |
                                          Q(character_status='inactive_player') |
                                          Q(character_status='dead_player'),
                                          blank=True)
    informed = models.ManyToManyField(Profile,
                                      related_name='described_events_informed',
                                      limit_choices_to=
                                      Q(character_status='active_player') |
                                      Q(character_status='inactive_player') |
                                      Q(character_status='dead_player'),
                                      blank=True)
    pictures = models.ManyToManyField(Picture, related_name='chronicle_events_pics', blank=True)

    def __str__(self):
        return f'{self.description[0:100]}...'

    class Meta:
        ordering = ['game_no', 'event_no_in_game']


class ChronicleEventNote(models.Model):
    author = models.ForeignKey(User, related_name='described_events_notes', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000, blank=True, null=True)
    event = models.ForeignKey(ChronicleEvent, related_name='notes', on_delete=models.PROTECT)
    color = models.CharField(max_length=20, choices=COLORS, default='#C70039')

    def __str__(self):
        return f'{self.text[0:50]}...'

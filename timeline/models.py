from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import Profile


SEASONS = (
    ('1', 'Wiosna'),
    ('2', 'Lato'),
    ('3', 'Jesień'),
    ('4', 'Zima')
)
COLORS = (
    ('#808080', 'szary'),
    ('#000000', 'czarny'),
    ('#C70039', 'czerwony'),
    ('#FFC300', 'pomarańczowy'),
    ('#229954', 'zielony'),
    ('#2e86c1', 'niebieski'),
    ('#000080', 'granatowy'),
    ('#800080', 'fioletowy')
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
    location_main = models.ForeignKey(GeneralLocation, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class GameSession(models.Model):
    game_no = models.PositiveSmallIntegerField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.game_no} - {self.title}'

    class Meta:
        ordering = ['game_no']


class DescribedEvent(models.Model):
    """
    This model is not connected with Event model. There is not 121 or M2M relationships between them.
    Event model serves to create events in timeline view (chronology).
    EventDescription serves to create events in the full history text of the game.
    Lack or correspondence between the two is intentional for flexibility.
    """
    game_no = models.ForeignKey(GameSession, related_name='described_events', blank=True, null=True, on_delete=models.CASCADE)
    description = models.TextField(max_length=4000)
    participants = models.ManyToManyField(Profile, related_name='described_events_participated',
                                          limit_choices_to={'character_status': 'player'}, blank=True)
    informed = models.ManyToManyField(Profile, related_name='described_events_informed',
                                      limit_choices_to={'character_status': 'player'}, blank=True)

    def __str__(self):
        return f'{self.description[0:50]}...'

    class Meta:
        ordering = ['game_no']


class Event(models.Model):
    year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    season = models.CharField(max_length=10, choices=SEASONS)
    day_start = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)])
    day_end = models.PositiveSmallIntegerField(blank=True, null=True,
                                               validators=[MinValueValidator(1), MaxValueValidator(90)])
    threads = models.ManyToManyField(Thread, related_name='events', blank=True)
    description = models.TextField(max_length=4000)
    participants = models.ManyToManyField(Profile, related_name='events_participated',
                                          limit_choices_to={'character_status': 'player'}, blank=True)
    informed = models.ManyToManyField(Profile, related_name='events_informed',
                                      limit_choices_to={'character_status': 'player'}, blank=True)
    general_location = models.ForeignKey(GeneralLocation, on_delete=models.CASCADE)
    specific_locations = models.ManyToManyField(SpecificLocation, related_name='events')
    game_no = models.ForeignKey(GameSession, related_name='events', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.description[0:50]}...'

    class Meta:
        ordering = ['year', 'season', 'day_start', 'day_end', 'id', 'game_no']

    # Steps to migrate these models:
    # 1) delete migration files, delete tables in db, DELETE FROM django_migrations WHERE app="timeline";
    # 2) comment out all other models than Event
    # 1) migrate Events without any M2M fields or ForeignKeys.
    # 2) uncomment other fields and classes and migrate.


class EventAnnotation(models.Model):
    author = models.ForeignKey(Profile, related_name='annotation_authors', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    event = models.ForeignKey(Event, related_name='annotations', on_delete=models.CASCADE)
    color = models.CharField(max_length=20, choices=COLORS)

    def __str__(self):
        return f'{self.text[0:50]}...'

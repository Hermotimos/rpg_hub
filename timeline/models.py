from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import Profile

SEASONS = (
    ('1', 'Wiosna'),
    ('2', 'Lato'),
    ('3', 'Jesień'),
    ('4', 'Zima')
)


class Event(models.Model):
    # TODO in templates: year + 19 ['rok Archonatu Nemetha Samatiana' jako dymek]
    year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    season = models.CharField(max_length=100, choices=SEASONS)
    day_start = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)])
    day_end = models.PositiveSmallIntegerField(blank=True, null=True,
                                               validators=[MinValueValidator(1), MaxValueValidator(90)])
    thread = models.CharField(max_length=200)
    description = models.TextField(max_length=4000)
    participants = models.ManyToManyField(to=Profile, related_name='events_participated',
                                          limit_choices_to={'character_status': 'player'}, blank=True)
    informed = models.ManyToManyField(to=Profile, related_name='events_informed',
                                      limit_choices_to={'character_status': 'player'}, blank=True)
    location1 = models.CharField(max_length=200)
    location2 = models.CharField(max_length=200)
    game_no = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.thread}: {self.description[0:20]}...'

    class Meta:
        ordering = ['year', 'season', 'day_start', 'day_end', 'thread']

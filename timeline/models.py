from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import Profile


class Event(models.Model):
    year = models.CharField(max_length=200)
    season = models.CharField(max_length=100)
    day_start = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)])
    day_end = models.PositiveSmallIntegerField(blank=True, null=True, default=day_start,
                                               validators=[MinValueValidator(1), MaxValueValidator(90)])
    thread = models.CharField(max_length=200)
    description = models.TextField(max_length=4000)
    participants = models.ManyToManyField(to=Profile, related_name='events_participated', blank=True, null=True)
    informed = models.ManyToManyField(to=Profile, related_name='events_informed', blank=True, null=True)
    location1 = models.CharField(max_length=200)
    location2 = models.CharField(max_length=200)
    game_no = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.thread}: {self.description[0:20]}...'

    class Meta:
        ordering = ['-day_start']

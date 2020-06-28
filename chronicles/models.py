from PIL import Image

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed

from debates.models import Debate
from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
from toponomikon.models import PrimaryLocation, SecondaryLocation
from users.models import Profile


class Date(models.Model):
    # TODO change order of fields year, season, day - easier dates only year
    SEASONS = (
        ('1', 'Wiosna'),
        ('2', 'Lato'),
        ('3', 'Jesień'),
        ('4', 'Zima')
    )
    day = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(90)],
        blank=True,
        null=True,
    )
    season = models.CharField(
        max_length=6,
        choices=SEASONS,
        blank=True,
        null=True,
    )
    year = models.IntegerField()
    
    class Meta:
        unique_together = ['year', 'season', 'day']

    def __str__(self):
        return str(self.year)


class EventType(models.Model):
    name = models.CharField(max_length=100)
    name_plural = models.CharField(max_length=100)
    order_no = models.PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class EventManager(models.Manager):
    
    def get_queryset(self):
        qs = super(EventManager, self).get_queryset()
        qs = qs.select_related(
            'in_event',
            'date_start',
            'date_end',
        ).prefetch_related(
            'events',
        )
        return qs
    
    
class Event(models.Model):
    # Manager
    objects = EventManager()
    # Fields
    name = models.CharField(max_length=256)
    name_genetive = models.CharField(max_length=256)
    description = models.TextField()
    type = models.ForeignKey(
        to=EventType,
        related_name='events',
        on_delete=models.PROTECT,
    )
    in_event = models.ForeignKey(
        to='self',
        related_name='events',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    date_start = models.ForeignKey(
        to=Date,
        related_name='events_started',
        on_delete=models.PROTECT,
        verbose_name='Date start (year of the encompassing unit)',
    )
    date_end = models.ForeignKey(
        to=Date,
        related_name='events_ended',
        on_delete=models.PROTECT,
        verbose_name='Date end (year of the encompassing unit)',
        blank=True,
        null=True,
    )
    primary_locations = models.ManyToManyField(
        to=PrimaryLocation,
        related_name='events_as_primary_loc',
    )
    secondary_locations = models.ManyToManyField(
        to=SecondaryLocation,
        related_name='events_as_secondary_loc',
        blank=True,
    )

    def __str__(self):
        res = str(self.name)
        if self.in_event and self.date_start:
            res += f' ({self.date_start}-)'
            if self.date_end:
                res = res[:-1] + f'{self.date_end}' + res[-1]
            if not self.events.all():
                res = res[:-2] + res[-1]
            res = res[:-1] + f' {self.in_event.name_genetive}' + res[-1]
        return res
    
    class Meta:
        ordering = ['type__order_no', 'date_start']
        unique_together = ['name', 'type']


# ----------------------------------------------------------------------------
# ---------------------------- PROXY MODELS-----------------------------------
# ----------------------------------------------------------------------------


class ChronologySystemManager(models.Manager):
    
    def get_queryset(self):
        qs = super(ChronologySystemManager, self).get_queryset()
        qs = qs.filter(Q(in_event=None))
        return qs
    
    
class ChronologySystem(Event):
    objects = ChronologySystemManager()
    
    class Meta:
        proxy = True
        verbose_name = 'I. Chronology system'


class EraManager(models.Manager):
    
    def get_queryset(self):
        qs = super(EraManager, self).get_queryset()
        qs = qs.select_related('in_event', 'date_start', 'date_end')
        qs = qs.prefetch_related('events')
        qs = qs.filter(
            ~Q(in_event=None) & Q(in_event__in_event=None)
        )
        return qs


class Era(Event):
    objects = EraManager()
    
    class Meta:
        proxy = True
        verbose_name = 'II. Era'


class PeriodManager(models.Manager):
    
    def get_queryset(self):
        qs = super(PeriodManager, self).get_queryset()
        qs = qs.select_related('in_event', 'date_start', 'date_end')
        qs = qs.prefetch_related('events')
        qs = qs.filter(
            ~Q(in_event=None) &
            ~Q(in_event__in_event=None) &
            Q(in_event__in_event__in_event=None) &
            ~Q(events=None)
        )
        return qs
    
    
class Period(Event):
    objects = PeriodManager()
    
    class Meta:
        proxy = True
        verbose_name = 'III. Period'


class SingularEventManager(models.Manager):
    
    def get_queryset(self):
        qs = super(SingularEventManager, self).get_queryset()
        qs = qs.select_related('in_event', 'date_start', 'date_end')
        qs = qs.prefetch_related('events')
        qs = qs.filter(events=None)
        return qs


class SingularEvent(Event):
    objects = SingularEventManager()
    
    class Meta:
        proxy = True
        verbose_name = 'IV. Singular Event'



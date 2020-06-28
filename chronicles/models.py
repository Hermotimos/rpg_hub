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


class Thread(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_ended = models.BooleanField(default=False)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(Thread, self).save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']
        verbose_name = '* Thread'


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
        verbose_name = '* Date'

    def __str__(self):
        return str(self.year)


class EventType(models.Model):
    name = models.CharField(max_length=100)
    name_plural = models.CharField(max_length=100)
    order_no = models.PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['name']
        verbose_name = '* Event type'

    def __str__(self):
        return str(self.name)


class EventManager(models.Manager):
    def get_queryset(self):
        qs = super(EventManager, self).get_queryset()
        qs = qs.select_related('in_event', 'date_start', 'date_end')
        qs = qs.prefetch_related('events')
        return qs
    
    
class Event(models.Model):
    # Manager
    objects = EventManager()
    # Fields
    name = models.CharField(max_length=256, blank=True, null=True)
    name_genetive = models.CharField(max_length=256, blank=True, null=True)
    description_short = models.TextField(unique=True, blank=True, null=True)
    description_long = models.TextField(unique=True, blank=True, null=True)
    threads = models.ManyToManyField(
        to=Thread,
        related_name='events',
        blank=True,
    )
    event_type = models.ForeignKey(
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
        #  TODO - blank and null are only for recreating events - delete later
        blank=True,
        null=True,

    )
    date_end = models.ForeignKey(
        to=Date,
        related_name='events_ended',
        on_delete=models.PROTECT,
        verbose_name='Date end (year of the encompassing unit)',
        blank=True,
        null=True,
    )
    known_directly = models.ManyToManyField(
        to=Profile,
        related_name='events_known_directly',
        limit_choices_to=
        Q(status='active_player')
        | Q(status='inactive_player')
        | Q(status='dead_player'),
        blank=True,
    )
    known_indirectly = models.ManyToManyField(
        to=Profile,
        related_name='events_known_indirectly',
        limit_choices_to=
        Q(status='active_player')
        | Q(status='inactive_player')
        | Q(status='dead_player'),
        blank=True,
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

    class Meta:
        ordering = ['event_type__order_no', 'date_start']
        unique_together = ['name', 'event_type']
        verbose_name = '-- Event'
        verbose_name_plural = '-- All Events'
        
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
    
    def informable(self):
        known_directly = self.known_directly.all()
        known_indirectly = self.known_indirectly.all()
        excluded = (known_directly | known_indirectly).distinct()
        informable = Profile.objects.filter(
            status='active_player'
        ).exclude(id__in=excluded)
        return informable


# ----------------------------------------------------------------------------
# ----------------------- PROXY MODELS FOR EVENT ------------------------------
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
        verbose_name = '1 - Chronology system'


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
        verbose_name = '2 - Era'


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
        verbose_name = '3 - Period'


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
        verbose_name = '4 - Singular Event'


# ----------------------------------------------------------------------------
# ---------------------------- GAME EVENTS -----------------------------------
# ----------------------------------------------------------------------------


class Chapter(models.Model):
    chapter_no = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=200, unique=True)
    image = models.ImageField(
        blank=True,
        null=True,
        upload_to='site_features_pics',
    )

    class Meta:
        ordering = ['chapter_no']
        verbose_name = 'I. Chapter'

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
    chapter = models.ForeignKey(
        to=Chapter,
        related_name='game_sessions',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['game_no']
        verbose_name = 'II. Game session'

    def __str__(self):
        return f'{self.game_no} - {self.title}'


class GameEvent(Event):
    game = models.ForeignKey(
        to=GameSession,
        related_name='game_events',
        on_delete=models.PROTECT,
        default=35,
    )
    event_no_in_game = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )
    pictures = models.ManyToManyField(
        to=Picture,
        related_name='game_events',
        blank=True,
    )
    debate = models.OneToOneField(
        to=Debate,
        related_name='game_event',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['game', 'event_no_in_game']
        verbose_name = 'III. Game event'

    def __str__(self):
        if self.description_short:
            return f'{self.description_short[:100]}'
        else:
            return f'{self.description_long[:100]}'
    


# TODO Create model with all nullable fields for users with History skill -
# TODO - so that they can place their own knowledge of events on the timeline


# def update_known_spec_locations(sender, instance, **kwargs):
#     """Whenever a profile becomes 'participant' or 'informed' of an event in
#     specific location add this location to profile's 'known_directly'
#     (if participant) or 'known_indirectly' (if informed).
#     """
#     participants = instance.participants.all()
#     informed = instance.informed.all()
#     spec_locations = instance.spec_locations.all()
#     for spec_location in spec_locations:
#         spec_location.known_directly.add(*participants)
#         spec_location.known_indirectly.add(*informed)
#
#
# post_save.connect(update_known_spec_locations, sender=TimelineEvent)
#
# # Run signal by each change of 'participants', 'informed' or 'spec_locations':
# m2m_changed.connect(update_known_spec_locations,
#                     sender=TimelineEvent.participants.through)
# m2m_changed.connect(update_known_spec_locations,
#                     sender=TimelineEvent.informed.through)
# m2m_changed.connect(update_known_spec_locations,
#                     sender=TimelineEvent.spec_locations.through)


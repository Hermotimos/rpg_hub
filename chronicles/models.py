from PIL import Image

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed

from debates.models import Debate
from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
from toponomikon.models import Location
from users.models import Profile

SEASONS = {
    '1': 'Wiosny',
    '2': 'Lata',
    '3': 'Jesieni',
    '4': 'Zimy'
}


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


class Thread(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_ended = models.BooleanField(default=False)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['sorting_name']
        verbose_name = '- Thread'


class Date(models.Model):
    SEASONS = (
        ('1', 'Wiosny'),
        ('2', 'Lata'),
        ('3', 'Jesieni'),
        ('4', 'Zimy')
    )
    
    year = models.IntegerField()
    season = models.CharField(
        max_length=6,
        choices=SEASONS,
        blank=True,
        null=True,
    )
    day = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(90)],
        blank=True,
        null=True,
    )
    
    class Meta:
        unique_together = ['year', 'season', 'day']
        verbose_name = '- Date'
    
    def __str__(self):
        if self.season and self.day:
            return f'{self.day}. dnia {SEASONS[self.season]} {self.year}. roku'
        elif self.season:
            return f'{SEASONS[self.season]} {self.year}. roku'
        return f'{self.year}. roku'
    

class TimeUnitManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'in_timeunit',
            # 'in_timeunit__in_timeunit',
            # 'in_timeunit__date_start',
            # 'in_timeunit__date_end',
            'date_start',
            'date_end',
            'debate',
        )
        return qs


class TimeUnit(models.Model):
    objects = TimeUnitManager()
    
    # All proxies
    date_start = models.ForeignKey(
        to=Date,
        related_name='timeunits_started',
        on_delete=models.PROTECT,
        verbose_name='Date start (year of the encompassing unit)',
        #  TODO - blank and null are only for recreating events - delete later
        blank=True,
        null=True,
    )
    date_end = models.ForeignKey(
        to=Date,
        related_name='timeunits_ended',
        on_delete=models.PROTECT,
        verbose_name='Date end (year of the encompassing unit)',
        blank=True,
        null=True,
    )
    in_timeunit = models.ForeignKey(
        to='self',
        related_name='timeunits',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    date_in_period = models.CharField(max_length=99, blank=True, null=True)
    date_in_era = models.CharField(max_length=99, blank=True, null=True)
    date_in_chronology = models.CharField(max_length=99, blank=True, null=True)
    description_short = models.TextField(blank=True, null=True)
    description_long = models.TextField(blank=True, null=True)
    
    # TimeSpan & HistoryEvent proxies
    known_short_desc = models.ManyToManyField(
        to=Profile,
        related_name='timeunits_known_short_desc',
        limit_choices_to=
        Q(status='active_player')
        | Q(status='inactive_player')
        | Q(status='dead_player'),
        blank=True,
    )
    known_long_desc = models.ManyToManyField(
        to=Profile,
        related_name='timeunits_long_desc',
        limit_choices_to=
        Q(status='active_player')
        | Q(status='inactive_player')
        | Q(status='dead_player'),
        blank=True,
    )

    # TimeSpan proxy
    name = models.CharField(max_length=256, blank=True, null=True)
    name_genetive = models.CharField(max_length=256, blank=True, null=True)

    # HistoryEvent & GameEvent proxies
    threads = models.ManyToManyField(
        to=Thread,
        related_name='events',
        blank=True,
    )
    locations = models.ManyToManyField(
        to=Location,
        related_name='events',
        blank=True,
    )

    # GameEvent proxy
    game = models.ForeignKey(
        to=GameSession,
        related_name='game_events',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    event_no_in_game = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
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
    pictures = models.ManyToManyField(
        to=Picture,
        related_name='events',
        blank=True,
    )
    debate = models.OneToOneField(
        to=Debate,
        related_name='event',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    
    class Meta:
        ordering = ['date_start']
        verbose_name_plural = '* Time Units (Time spans, History events, Game events)'
    
    def __str__(self):
        res = str(self.name)
        if self.in_timeunit and self.date_start:
            res += f' ({self.date_start.year}-)'
            if self.date_end:
                res = res[:-1] + f'{self.date_end.year}' + res[-1]
            if not self.timeunits.all():
                res = res[:-2] + res[-1]
            res = res[:-1] + f' | {self.in_timeunit.name_genetive}' + res[-1]
        return res
    
    def informables(self):
        qs = Profile.objects.filter(status__in=[
            'active_player',
        ])
        qs = qs.exclude(
            id__in=(self.known_directly.all() | self.known_indirectly.all())
        )
        return qs

    def save(self, *args, **kwargs):
        start = self.date_start
        end = self.date_end
        dates = start or '???'
        if end:
            if end.year and end.season:
                if end.season == start.season and end.year == start.year:
                    dates = f'{start.day}-{end}'
                elif end.year == start.year:
                    dates = f'{start.day}. dnia {start.season} - {end}'
                else:
                    dates = f'{start} - {end}'
        self.dates = str(dates) + ' ' + str(self.in_timeunit.name_genetive)
        super().save(*args, **kwargs)

# ----------------------------------------------------------------------------
# -------------------------------- PROXIES -----------------------------------
# ----------------------------------------------------------------------------


class ChronologyManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related()
        qs = qs.prefetch_related('timeunits')
        qs = qs.filter(Q(in_timeunit=None))
        return qs


class Chronology(TimeUnit):
    objects = ChronologyManager()
    
    class Meta:
        proxy = True
        verbose_name_plural = '1 - Chronologies'


class EraManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related()
        qs = qs.prefetch_related('timeunits')
        qs = qs.filter(~Q(in_timeunit=None) & Q(in_timeunit__in_timeunit=None))
        return qs


class Era(TimeUnit):
    objects = EraManager()
    
    class Meta:
        proxy = True
        ordering = ['in_timeunit']
        verbose_name = '2 - Era'


class PeriodManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related()
        qs = qs.prefetch_related('timeunits')
        qs = qs.filter(
            ~Q(in_timeunit=None)
            & ~Q(in_timeunit__in_timeunit=None)
            & Q(in_timeunit__in_timeunit__in_timeunit=None)
            # & ~Q(events=None)
        )
        return qs


class Period(TimeUnit):
    objects = PeriodManager()
    
    class Meta:
        proxy = True
        ordering = ['in_timeunit']
        verbose_name = '3 - Period'


class Event(TimeUnit):
    """Proxy model to add save() method for GameEvents and HistoryEvents."""
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        start = self.date_start
        end = self.date_end
        start_day = end_day = ''
        start_season = end_season = ''
        start_year_in_period = end_year_in_period = ''
        
        if start:
            start_day = f'{start.day}' if start.day else ''
            start_season = f'{SEASONS[start.season]}' if start.season else ''
            start_year_in_period = f'{start.year}'
        if end:
            end_day = f'{end.day}' if end.day else ''
            end_season = f'{SEASONS[end.season]}' if end.season else ''
            end_year_in_period = f'{end.year}'
            
        # Date in period
        period = self.in_timeunit
        if not end:
            prefix = f'{start_day}. dnia {start_season}'
            date_in_period = f'{start}'
        else:
            if start_year_in_period != end_year_in_period:
                prefix = None                   # is overriden with prefix_yr1 etc.
                date_in_period = f'{start} - {end}'
            elif start_season != end_season:
                prefix_s1 = f'{start_day}. dnia {start_season}'
                prefix_s2 = f'{end_day}. dnia {end_season}'
                prefix = prefix_s1 + ' - ' + prefix_s2
                date_in_period = f'{start_day}. dnia {start_season} - {end}'
            elif start_day != end_day:
                prefix = f'{start_day}-{end_day}. dnia {end_season}'
                date_in_period = f'{start_day}-{end}'
            else:
                prefix = f'{start_day}. dnia {start_season}'
                date_in_period = f'{start}'
        date_in_period += f' {period.name_genetive}'

        # Date in era
        era = self.in_timeunit.in_timeunit
        period_begin_in_era = period.date_start.year
        start_year_in_era = int(period_begin_in_era) + int(start_year_in_period)
        
        if not end:
            date_in_era = f'{prefix} {start_year_in_era}. roku {era.name_genetive}'
        else:
            end_year_in_era = int(period_begin_in_era) + int(end_year_in_period)
            if start_year_in_period != end_year_in_period:
                prefix_yr1 = f'{start_day}. dnia {start_season}'
                prefix_yr2 = f'{end_day}. dnia {end_season}'
                date_in_era = f'{prefix_yr1} {start_year_in_era}. roku'
                date_in_era += f' - {prefix_yr2} {end_year_in_era}. roku '
            else:
                date_in_era = f'{prefix} {start_year_in_era}. roku '
            date_in_era += f'{era.name_genetive}'
            
        # Date in chronology
        chronology = self.in_timeunit.in_timeunit.in_timeunit
        era_begin_in_chronology = era.date_start.year
        start_year_in_chronology = int(era_begin_in_chronology) + int(period_begin_in_era) + int(start_year_in_period)
        
        if not end:
            date_in_chronology = f'{prefix} {start_year_in_chronology}. roku {chronology.name_genetive}'
        else:
            end_year_in_chronology = int(era_begin_in_chronology) + int(period_begin_in_era) + int(end_year_in_period)
            if start_year_in_period != end_year_in_period:
                prefix_yr1 = f'{start_day}. dnia {start_season}'
                prefix_yr2 = f'{end_day}. dnia {end_season}'
                date_in_chronology = f'{prefix_yr1} {start_year_in_chronology}. roku'
                date_in_chronology += f' - {prefix_yr2} {end_year_in_chronology}. roku '
            else:
                date_in_chronology = f'{prefix} {start_year_in_chronology}. roku '
            date_in_chronology += f'{chronology.name_genetive}'
            
        self.date_in_period = str(date_in_period)
        self.date_in_era = str(date_in_era)
        self.date_in_chronology = str(date_in_chronology)
        super().save(*args, **kwargs)


class HistoryEventManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related()
        qs = qs.filter(Q(game=None), timeunits=None)
        return qs


class HistoryEvent(Event):
    objects = HistoryEventManager()
    
    class Meta:
        proxy = True
        verbose_name = '4 - History Event'
    
    def __str__(self):
        return self.description_short or str(self.pk)


class GameEventManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('game', 'in_timeunit', 'date_start', 'date_end',
                               'debate')
        qs = qs.filter(~Q(game=None))
        return qs


class GameEvent(Event):
    objects = GameEventManager()
    
    class Meta:
        proxy = True
        ordering = ['game', 'event_no_in_game']
        verbose_name = 'III. Game event'
    
    def __str__(self):
        # return self.description_short or str(self.pk)     # TODO after transition is done
        return self.description_long[:100] or str(self.pk)


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


from PIL import Image

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    BooleanField,
    CharField,
    DateField,
    ForeignKey as FK,
    ImageField,
    IntegerField,
    Manager,
    ManyToManyField as M2MField,
    Model,
    PositiveSmallIntegerField,
    PROTECT,
    Q,
    TextField,
)
from django.db.models.signals import post_save, m2m_changed

from debates.models import Debate
from imaginarion.models import Picture, Audio, PictureSet
from rpg_project.utils import create_sorting_name
from toponomikon.models import Location
from users.models import Profile


SEASONS = {
    '1': 'Wiosny',
    '2': 'Lata',
    '3': 'Jesieni',
    '4': 'Zimy'
}


class Chapter(Model):
    chapter_no = IntegerField(blank=True, null=True)
    title = CharField(max_length=200, unique=True)
    image = ImageField(upload_to='site_features_pics', blank=True, null=True)
    
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


class GameSession(Model):
    game_no = IntegerField(null=True)
    title = CharField(max_length=200)
    chapter = FK(
        to=Chapter,
        related_name='game_sessions',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    date = DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['game_no']
        verbose_name = 'II. Game session'
    
    def __str__(self):
        return self.title


class Thread(Model):
    name = CharField(max_length=100, unique=True)
    is_ended = BooleanField(default=False)
    sorting_name = CharField(max_length=250, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['sorting_name']
        verbose_name = '- Thread'


class ThreadActiveManager(Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_ended=False)
        return qs


class ThreadActive(Thread):
    objects = ThreadActiveManager()
    
    class Meta:
        proxy = True
        verbose_name = '- Active Thread'
        verbose_name_plural = '- Threads Active'


class ThreadEndedManager(Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_ended=True)
        return qs


class ThreadEnded(Thread):
    objects = ThreadEndedManager()
    
    class Meta:
        proxy = True
        verbose_name = '- Ended Thread'
        verbose_name_plural = '- Threads Ended'


class Date(Model):
    SEASONS = (
        ('1', 'Wiosny'),
        ('2', 'Lata'),
        ('3', 'Jesieni'),
        ('4', 'Zimy')
    )
    
    year = IntegerField()
    season = CharField(max_length=6, choices=SEASONS, blank=True, null=True)
    day = PositiveSmallIntegerField(
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
    

class TimeUnitManager(Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'in_timeunit',
            # 'in_timeunit__in_timeunit',
            # 'in_timeunit__date_start',
            # 'in_timeunit__date_end',
            'date_start',
            'date_end',
        )
        qs = qs.prefetch_related('timeunits')
        return qs


class TimeUnit(Model):
    objects = TimeUnitManager()
    
    # Fields for all proxies
    date_start = FK(
        to=Date,
        related_name='timeunits_started',
        on_delete=PROTECT,
        verbose_name='Date start (year of the encompassing unit)',
        #  TODO - blank and null are only for recreating events - delete later
        blank=True,
        null=True,
    )
    date_end = FK(
        to=Date,
        related_name='timeunits_ended',
        on_delete=PROTECT,
        verbose_name='Date end (year of the encompassing unit)',
        blank=True,
        null=True,
    )
    in_timeunit = FK(
        to='self',
        related_name='timeunits',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    date_in_period = CharField(max_length=99, blank=True, null=True)
    date_in_era = CharField(max_length=99, blank=True, null=True)
    date_in_chronology = CharField(max_length=99, blank=True, null=True)
    description_short = TextField(blank=True, null=True)
    description_long = TextField(blank=True, null=True)
    
    # Fields for TimeSpan & HistoryEvent proxies
    known_short_desc = M2MField(
        to=Profile,
        related_name='timeunits_known_short_desc',
        # limit_choices_to=PLAYERS,
        limit_choices_to=Q(status='player'),
        blank=True,
    )
    known_long_desc = M2MField(
        to=Profile,
        related_name='timeunits_long_desc',
        # limit_choices_to=PLAYERS,
        limit_choices_to=Q(status='player'),
        blank=True,
    )

    # Fields for TimeSpan proxy
    name = CharField(max_length=256, blank=True, null=True)
    name_genetive = CharField(max_length=256, blank=True, null=True)

    # Fields for HistoryEvent & GameEvent proxies
    threads = M2MField(to=Thread, related_name='events', blank=True)
    locations = M2MField(to=Location, related_name='events', blank=True)
    audio = FK(
        to=Audio,
        related_name='events',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )

    # GameEvent proxy
    game = FK(
        to=GameSession,
        related_name='game_events',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    event_no_in_game = PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        blank=True,
        null=True,
    )
    known_directly = M2MField(
        to=Profile,
        related_name='events_known_directly',
        # limit_choices_to=PLAYERS,
        limit_choices_to=Q(status='player'),
        blank=True,
    )
    known_indirectly = M2MField(
        to=Profile,
        related_name='events_known_indirectly',
        # limit_choices_to=PLAYERS,
        limit_choices_to=Q(status='player'),
        blank=True,
    )
    pictures = M2MField(to=Picture, related_name='events', blank=True)
    picture_sets = M2MField(to=PictureSet, related_name='events', blank=True)
    debates = M2MField(to=Debate, related_name='events', blank=True)
    
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
                res = res[:-1] + res[-1]
            res = res[:-1] + f' | {self.in_timeunit.name_genetive}' + res[-1]
        return res
    
    def informables(self):
        qs = Profile.active_players.all()
        qs = qs.exclude(
            id__in=(self.known_directly.all() | self.known_indirectly.all())
        )
        return qs


# ----------------------------------------------------------------------------
# -------------------------------- PROXIES -----------------------------------
# ----------------------------------------------------------------------------


class ChronologyManager(Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('in_timeunit', 'date_start', 'date_end')
        qs = qs.prefetch_related('timeunits')
        qs = qs.filter(Q(in_timeunit=None))
        return qs


class Chronology(TimeUnit):
    objects = ChronologyManager()
    
    class Meta:
        proxy = True
        verbose_name_plural = '1 - Chronologies'


class EraManager(Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('in_timeunit', 'date_start', 'date_end')
        qs = qs.prefetch_related('timeunits')
        qs = qs.filter(~Q(in_timeunit=None) & Q(in_timeunit__in_timeunit=None))
        return qs


class Era(TimeUnit):
    objects = EraManager()
    
    class Meta:
        proxy = True
        ordering = ['in_timeunit']
        verbose_name = '2 - Era'


class PeriodManager(Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('in_timeunit', 'date_start', 'date_end')
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
    """Intermediary proxy to add shared methods to Game- and HistoryEvents."""
    class Meta:
        proxy = True

    def __str__(self):
        return self.description_short or str(self.pk)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        start = self.date_start
        end = self.date_end
        start_day = end_day = 0
        start_season = end_season = 0
        start_year_in_period = end_year_in_period = 0
        
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


class HistoryEventManager(Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'in_timeunit', 'date_start', 'date_end', 'audio')
        qs = qs.filter(Q(game=None), timeunits=None)
        return qs


class HistoryEvent(Event):
    objects = HistoryEventManager()
    
    class Meta:
        proxy = True
        verbose_name = '4 - History Event'
    

class GameEventManager(Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'game', 'in_timeunit', 'date_start', 'date_end', 'audio')
        qs = qs.filter(~Q(game=None))
        return qs


class GameEvent(Event):
    objects = GameEventManager()
    
    class Meta:
        proxy = True
        ordering = ['game', 'event_no_in_game']
        verbose_name = 'III. Game event'
    

def update_known_locations(sender, instance, **kwargs):
    """Whenever a profile becomes 'participant' or 'informed' of an event in
    specific location add this location to profile's 'known_directly'
    (if participant) or 'known_indirectly' (if informed).
    """
    known_directly = instance.known_directly.all()
    known_indirectly = instance.known_indirectly.all()
    locations = instance.locations.all()
    for location in locations:
        location.known_directly.add(*known_directly)
        location.known_indirectly.add(*known_indirectly)


post_save.connect(update_known_locations, sender=GameEvent)

# Run by each change of 'known_directly', 'known_indirectly' or 'locations':
m2m_changed.connect(update_known_locations,
                    sender=GameEvent.known_directly.through)
m2m_changed.connect(update_known_locations,
                    sender=GameEvent.known_indirectly.through)
m2m_changed.connect(update_known_locations,
                    sender=GameEvent.locations.through)


from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    BooleanField,
    CharField,
    DateField,
    ForeignKey as FK,
    ImageField,
    IntegerField,
    Manager,
    ManyToManyField as M2M,
    Model,
    PositiveSmallIntegerField,
    PROTECT,
    Q,
    TextField,
)
from django.db.models.signals import post_save, m2m_changed
from django.utils.text import Truncator
from django.contrib.postgres.fields import ArrayField
from communications.models import Thread
from imaginarion.models import Audio, PictureSet
from rpg_project.utils import OrderByPolish
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
    image = ImageField(upload_to='chronicles', blank=True, null=True)

    class Meta:
        ordering = ['chapter_no']
        verbose_name = 'I. Chapter'

    def __str__(self):
        return self.title


class GameSession(Model):
    order_no = IntegerField(null=True)
    title = CharField(max_length=200)
    chapter = FK(
        to=Chapter,
        related_name='game_sessions',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    game_no = IntegerField(null=True)
    date = DateField(blank=True, null=True)

    class Meta:
        ordering = ['order_no']
        verbose_name = 'II. Game session'

    def __str__(self):
        return self.title


class PlotThreadManager(Manager):
    pass


class PlotThreadEndedManager(Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_ended=True)
        return qs


class PlotThreadActiveManager(Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_ended=False)
        return qs


class PlotThread(Model):
    name = CharField(max_length=100, unique=True)
    is_ended = BooleanField(default=False)

    objects = PlotThreadManager()
    plot_threads_ended = PlotThreadEndedManager()
    plot_threads_active = PlotThreadActiveManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = [OrderByPolish('name')]
        verbose_name = '- PlotThread'


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
        ordering = ['year', 'day']

    def __str__(self):
        if self.season and self.day:
            return f'{self.day} dnia {SEASONS[self.season]} {self.year} roku'
        elif self.season:
            return f'{SEASONS[self.season]} {self.year} roku'
        return f'{self.year} roku'


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


def non_GM():
    non_GM = Profile.non_gm.all()
    return Q(id__in=non_GM)


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
    known_short_desc = M2M(
        to=Profile,
        related_name='timeunits_known_short_desc',
        blank=True,
    )
    known_long_desc = M2M(
        to=Profile,
        related_name='timeunits_long_desc',
        blank=True,
    )

    # Fields for TimeSpan proxy
    name = CharField(max_length=256, blank=True, null=True)
    name_genetive = CharField(max_length=256, blank=True, null=True)

    # Fields for HistoryEvent & GameEvent proxies
    plot_threads = M2M(to=PlotThread, related_name='events', blank=True)
    locations = M2M(to=Location, related_name='events', blank=True)
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
    participants = M2M(
        to=Profile,
        related_name='events_participated',
        limit_choices_to=non_GM,
        blank=True,
    )
    informees = M2M(
        to=Profile,
        related_name='events_informed',
        limit_choices_to=non_GM,
        blank=True,
    )
    picture_sets = M2M(to=PictureSet, related_name='events', blank=True)
    debates = M2M(
        to=Thread,
        related_name='events',
        limit_choices_to={'kind': 'Debate'},
        blank=True)

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

    def informables(self, current_profile):
        qs = current_profile.character.acquaintanceships()
        qs = qs.exclude(
            known_character__profile__in=(self.participants.all() | self.informees.all())
        ).filter(
            known_character__profile__in=Profile.active_players.all())

        # TODO temp 'Ilen z Astinary, Alora z Astinary'
        # hide Davos from Ilen and Alora
        if current_profile.id in [5, 6]:
            qs = qs.exclude(known_character__profile__id=3)
        # vice versa
        if current_profile.id == 3:
            qs = qs.exclude(known_character__profile__id__in=[5, 6])
        # TODO end temp

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
        return Truncator(self.description_short).words(15) or str(self.pk)

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
            prefix = f'{start_day} dnia {start_season}'
            date_in_period = f'{start}'
        else:
            if start_year_in_period != end_year_in_period:
                prefix = None                   # is overriden with prefix_yr1 etc.
                date_in_period = f'{start} - {end}'
            elif start_season != end_season:
                prefix_s1 = f'{start_day} dnia {start_season}'
                prefix_s2 = f'{end_day} dnia {end_season}'
                prefix = prefix_s1 + ' - ' + prefix_s2
                date_in_period = f'{start_day} dnia {start_season} - {end}'
            elif start_day != end_day:
                prefix = f'{start_day}-{end_day} dnia {end_season}'
                date_in_period = f'{start_day}-{end}'
            else:
                prefix = f'{start_day} dnia {start_season}'
                date_in_period = f'{start}'
        date_in_period += f' {period.name_genetive}'

        # Date in era
        era = self.in_timeunit.in_timeunit
        period_begin_in_era = period.date_start.year
        start_year_in_era = int(period_begin_in_era) + int(start_year_in_period)

        if not end:
            date_in_era = f'{prefix} {start_year_in_era} roku {era.name_genetive}'
        else:
            end_year_in_era = int(period_begin_in_era) + int(end_year_in_period)
            if start_year_in_period != end_year_in_period:
                prefix_yr1 = f'{start_day} dnia {start_season}'
                prefix_yr2 = f'{end_day} dnia {end_season}'
                date_in_era = f'{prefix_yr1} {start_year_in_era} roku'
                date_in_era += f' - {prefix_yr2} {end_year_in_era} roku '
            else:
                date_in_era = f'{prefix} {start_year_in_era} roku '
            date_in_era += f'{era.name_genetive}'

        # Date in chronology
        chronology = self.in_timeunit.in_timeunit.in_timeunit
        era_begin_in_chronology = era.date_start.year
        start_year_in_chronology = int(era_begin_in_chronology) + int(period_begin_in_era) + int(start_year_in_period)

        if not end:
            date_in_chronology = f'{prefix} {start_year_in_chronology} roku {chronology.name_genetive}'
        else:
            end_year_in_chronology = int(era_begin_in_chronology) + int(period_begin_in_era) + int(end_year_in_period)
            if start_year_in_period != end_year_in_period:
                prefix_yr1 = f'{start_day} dnia {start_season}'
                prefix_yr2 = f'{end_day} dnia {end_season}'
                date_in_chronology = f'{prefix_yr1} {start_year_in_chronology} roku'
                date_in_chronology += f' - {prefix_yr2} {end_year_in_chronology} roku '
            else:
                date_in_chronology = f'{prefix} {start_year_in_chronology} roku '
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
    specific location add this location to profile's 'participants'
    (if participant) or 'informees' (if informed).
    """
    participants = instance.participants.all()
    informees = instance.informees.all()
    locations = instance.locations.all()
    for location in locations:
        location.participants.add(*participants)
        location.informees.add(*informees)


post_save.connect(
    receiver=update_known_locations,
    sender=GameEvent)

# Run by each change of 'participants', 'informees' or 'locations':
m2m_changed.connect(
    receiver=update_known_locations,
    sender=GameEvent.participants.through)

m2m_changed.connect(
    receiver=update_known_locations,
    sender=GameEvent.informees.through)

m2m_changed.connect(
    receiver=update_known_locations,
    sender=GameEvent.locations.through)


def update_acquantanceships_for_participants(sender, instance, **kwargs):
    """Whenever GameEvent is saved (create & update), create Acquaintanceship
    objects for all participants, in both directions.
    """
    from prosoponomikon.models import Acquaintanceship, Character

    participating_characters = Character.objects.filter(
        profile__in=instance.participants.all())

    for knowing_character in participating_characters:
        for known_character in participating_characters.exclude(id=knowing_character.id):

            existing, created = Acquaintanceship.objects.get_or_create(
                knowing_character=knowing_character,
                known_character=known_character,
                defaults={"is_direct": True})

            if not existing.is_direct:
                existing.is_direct = True
                existing.save()


# This signal also fires on GameEvent object creation
m2m_changed.connect(
    receiver=update_acquantanceships_for_participants,
    sender=GameEvent.participants.through)


def update_acquantanceships_for_informees(sender, instance, **kwargs):
    """Whenever GameEvent is saved (create & update), create Acquaintanceship
    objects for all informees, so that they know all participants indirectly.
    """
    from prosoponomikon.models import Acquaintanceship, Character

    characters = Character.objects.all()
    participating_characters = characters.filter(profile__in=instance.participants.all())
    informed_characters = characters.filter(profile__in=instance.informees.all())

    for knowing_character in informed_characters:
        for known_character in participating_characters:
            Acquaintanceship.objects.get_or_create(
                knowing_character=knowing_character,
                known_character=known_character,
                defaults={'is_direct': False},
            )


# This signal also fires on GameEvent object creation
m2m_changed.connect(
    receiver=update_acquantanceships_for_informees,
    sender=GameEvent.informees.through)

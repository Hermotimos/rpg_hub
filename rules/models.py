from django.db.models import (
    CharField,
    DecimalField,
    ForeignKey as FK,
    ImageField,
    Manager,
    ManyToManyField as M2MField,
    Model,
    PositiveSmallIntegerField,
    PROTECT,
    TextField,
)
from django.db.models import Q

from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
from users.models import Profile


class Skill(Model):
    name = CharField('Umiejętność', max_length=100, unique=True)
    tested_trait = CharField('Cecha/Cechy', max_length=50, blank=True, null=True)
    image = ImageField(upload_to='site_features_pics', blank=True, null=True)
    allowed_profiles = M2MField(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_skills',
        blank=True,
    )
    sorting_name = CharField(max_length=101, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    class Meta:
        ordering = ['sorting_name']


S_LEVELS = [
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3')
]


class SkillLevel(Model):
    skill = FK(to=Skill, related_name='skill_levels', on_delete=PROTECT)
    level = CharField(max_length=10, choices=S_LEVELS)
    description = TextField(max_length=4000, blank=True, null=True)
    acquired_by = M2MField(to=Profile, related_name='skill_levels', blank=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f'{str(self.skill.name)} [{self.level}]'

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']


class TheologySkillManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(name__icontains='Doktryn')
                       | Q(name__icontains='Kult')
                       | Q(name__icontains='Wierzenia')
                       | Q(name__icontains='Teolog'))
        return qs
    

class TheologySkill(Skill):
    objects = TheologySkillManager()
    
    class Meta:
        proxy = True
        verbose_name = 'Teologia'
        verbose_name_plural = 'Skills - THEOLOGY'


class BooksSkillManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(name__icontains='Księg'))
        return qs
    

class BooksSkill(Skill):
    objects = BooksSkillManager()

    class Meta:
        proxy = True
        verbose_name = 'Księgi'
        verbose_name_plural = 'Skills - BOOKS'


class HistorySkillManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(name__icontains='Histor'))
        return qs
    

class HistorySkill(Skill):
    objects = HistorySkillManager()

    class Meta:
        proxy = True
        verbose_name = 'Historia'
        verbose_name_plural = 'Skills - HISTORY'


class Synergy(Model):
    name = CharField(max_length=100, verbose_name='Synergia')
    skills = M2MField(to=Skill, related_name='skills')
    allowed_profiles = M2MField(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_synergies',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'synergy'
        verbose_name_plural = 'synergies'


class SynergyLevel(Model):
    synergy = FK(to=Synergy, related_name='synergy_levels', on_delete=PROTECT)
    level = CharField(max_length=10, choices=S_LEVELS[1:])
    description = TextField(max_length=4000, blank=True, null=True)
    acquired_by = M2MField(
        to=Profile,
        related_name='synergy_levels',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f'{str(self.synergy.name)} [{self.level}]'

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']


class Profession(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    def allowed_list(self):
        allowed_profiles = []
        for klass in self.klasses.all():
            for profile in klass.allowed_profiles.all():
                allowed_profiles.append(profile)
        return allowed_profiles

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Profession'
        verbose_name_plural = 'Professions'


class Klass(Model):
    name = CharField(max_length=100, unique=True)
    profession = FK(to=Profession, related_name='klasses', on_delete=PROTECT)
    description = TextField(max_length=4000, blank=True, null=True)
    start_perks = TextField(max_length=4000, blank=True, null=True)
    lvl_1 = CharField(max_length=500, blank=True, null=True)
    lvl_2 = CharField(max_length=500, blank=True, null=True)
    lvl_3 = CharField(max_length=500, blank=True, null=True)
    lvl_4 = CharField(max_length=500, blank=True, null=True)
    lvl_5 = CharField(max_length=500, blank=True, null=True)
    lvl_6 = CharField(max_length=500, blank=True, null=True)
    lvl_7 = CharField(max_length=500, blank=True, null=True)
    lvl_8 = CharField(max_length=500, blank=True, null=True)
    lvl_9 = CharField(max_length=500, blank=True, null=True)
    lvl_10 = CharField(max_length=500, blank=True, null=True)
    lvl_11 = CharField(max_length=500, blank=True, null=True)
    lvl_12 = CharField(max_length=500, blank=True, null=True)
    lvl_13 = CharField(max_length=500, blank=True, null=True)
    lvl_14 = CharField(max_length=500, blank=True, null=True)
    lvl_15 = CharField(max_length=500, blank=True, null=True)
    lvl_16 = CharField(max_length=500, blank=True, null=True)
    lvl_17 = CharField(max_length=500, blank=True, null=True)
    lvl_18 = CharField(max_length=500, blank=True, null=True)
    lvl_19 = CharField(max_length=500, blank=True, null=True)
    lvl_20 = CharField(max_length=500, blank=True, null=True)
    allowed_profiles = M2MField(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_klasses',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Klass'
        verbose_name_plural = 'Klasses'


class EliteProfession(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = M2MField(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_elite_classes',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Elite profession'
        verbose_name_plural = 'Elite professions'


class EliteKlass(Model):
    name = CharField(max_length=100, unique=True)
    elite_profession = FK(
        to=EliteProfession,
        related_name='elite_klasses',
        on_delete=PROTECT,
    )
    description = TextField(max_length=4000, blank=True, null=True)
    start_perks = TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = M2MField(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_elite_klasses',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Elite klass'
        verbose_name_plural = 'Elite klasses'


class WeaponType(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Weapon type'
        verbose_name_plural = 'Weapon types'


DAMAGE_TYPES = [
    ('K', 'K'),
    ('S', 'S'),
    ('O', 'O'),
    ('K/S', 'K/S'),
    ('K/O', 'K/O'),
    ('O/S', 'O/S'),
    ('K/S/O', 'K/S/O')
]
TRAITS = [
    ('Sił', 'Sił'),
    ('Zrc', 'Zrc'),
    ('Sił/Zrc', 'Sił/Zrc')
]
SIZES = [
    ('M', 'M'),
    ('Ś', 'Ś'),
    ('D', 'D')
]
CURRENCIES = [
    ('m', 'm'),
    ('ss', 'ss'),
    ('sz', 'sz'),
    ('sp', 'sp'),
]


class Weapon(Model):
    weapon_type = FK(to=WeaponType, related_name='weapons', on_delete=PROTECT)
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    pictures = M2MField(to=Picture, related_name='weapon_pics', blank=True)
    delay = PositiveSmallIntegerField()
    damage_small_dices = CharField(max_length=10, blank=True, null=True)
    damage_small_add = PositiveSmallIntegerField(blank=True, null=True)
    damage_big_dices = CharField(max_length=10, blank=True, null=True)
    damage_big_add = PositiveSmallIntegerField(blank=True, null=True)
    damage_type = CharField(max_length=10, choices=DAMAGE_TYPES)
    special = TextField(max_length=4000, blank=True, null=True)
    range = CharField(max_length=100, blank=True, null=True)
    size = CharField(max_length=5, choices=SIZES)
    trait = CharField(max_length=10, choices=TRAITS)
    avg_price_value = PositiveSmallIntegerField(blank=True, null=True)
    avg_price_currency = CharField(max_length=5, choices=CURRENCIES, blank=True, null=True)
    avg_weight = DecimalField(max_digits=10, decimal_places=1)

    allowed_profiles = M2MField(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_weapons',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    def damage_summary(self):
        damage_small = str(self.damage_small_dices)
        if self.damage_small_add:
            damage_small += ('+' + str(self.damage_small_add))
        damage_big = str(self.damage_big_dices)
        if self.damage_big_add:
            damage_big += ('+' + str(self.damage_big_add))
        return f'{damage_small}/{damage_big}'

    class Meta:
        ordering = ['sorting_name']


class Plate(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    pictures = M2MField(to=Picture, related_name='plate_pics', blank=True)
    armor_class_bonus = PositiveSmallIntegerField(blank=True, null=True)
    parrying = PositiveSmallIntegerField(blank=True, null=True)
    endurance = PositiveSmallIntegerField()
    weight = DecimalField(max_digits=10, decimal_places=1)

    mod_max_agility = PositiveSmallIntegerField(blank=True, null=True)
    mod_max_movement = CharField(max_length=2, blank=True, null=True)

    mod_pickpocketing = DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_lockpicking = DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_sneaking_towns = DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_sneaking_wilderness = DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_hiding_towns = DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_hiding_wilderness = DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_climbing = DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_traps = DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    allowed_profiles = M2MField(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_plates',
        blank=True,
    )
    sorting_number = DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.name

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    class Meta:
        ordering = ['sorting_number']


class Shield(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    pictures = M2MField(to=Picture, related_name='shield_pics', blank=True)
    enemies_no = PositiveSmallIntegerField()
    armor_class_bonus_close_combat = PositiveSmallIntegerField(
        blank=True,
        null=True,
    )
    armor_class_bonus_distance_combat = PositiveSmallIntegerField(
        blank=True,
        null=True,
    )
    weight = DecimalField(max_digits=10, decimal_places=1)

    allowed_profiles = M2MField(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_shields',
        blank=True,
    )
    sorting_number = DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sorting_number']

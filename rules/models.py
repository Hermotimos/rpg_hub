from django.db import models
from django.db.models import Q

from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
from users.models import Profile


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Umiejętność')
    tested_trait = models.CharField(max_length=50, verbose_name='Cecha/Cechy',
                                    blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='site_features_pics')
    allowed_profiles = models.ManyToManyField(to=Profile, blank=True,
                                              limit_choices_to=Q(status='active_player') |
                                                               Q(status='inactive_player') |
                                                               Q(status='dead_player'),
                                              related_name='allowed_skills')
    sorting_name = models.CharField(max_length=101, blank=True, null=True)

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


class SkillLevel(models.Model):
    skill = models.ForeignKey(to=Skill, related_name='skill_levels', on_delete=models.PROTECT)
    level = models.CharField(max_length=10, choices=S_LEVELS)
    description = models.TextField(max_length=4000, blank=True, null=True)
    acquired_by = models.ManyToManyField(to=Profile,
                                         related_name='skill_levels',
                                         blank=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f'{str(self.skill.name)} [{self.level}]'

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']


class TheologySkillManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(name__icontains='Doktryn')
                       | Q(name__icontains='Kult')
                       | Q(name__icontains='Teolog'))
        return qs
    

class TheologySkill(Skill):
    objects = TheologySkillManager()
    
    class Meta:
        proxy = True
        verbose_name = 'Skills - THEOLOGY'
        verbose_name_plural = 'Skills - THEOLOGY'


class BooksSkillManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(name__icontains='Księg'))
        return qs
    

class BooksSkill(Skill):
    objects = BooksSkillManager()

    class Meta:
        proxy = True
        verbose_name = 'Skills - BOOKS'
        verbose_name_plural = 'Skills - BOOKS'


class Synergy(models.Model):
    name = models.CharField(max_length=100, verbose_name='Synergia')
    skills = models.ManyToManyField(Skill, related_name='skills')
    allowed_profiles = models.ManyToManyField(to=Profile, blank=True,
                                              limit_choices_to=Q(status='active_player') |
                                                               Q(status='inactive_player') |
                                                               Q(status='dead_player'),
                                              related_name='allowed_synergies')
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

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


class SynergyLevel(models.Model):
    synergy = models.ForeignKey(Synergy, related_name='synergy_levels', on_delete=models.PROTECT)
    level = models.CharField(max_length=10, choices=S_LEVELS[1:])
    description = models.TextField(max_length=4000, blank=True, null=True)
    acquired_by = models.ManyToManyField(to=Profile,
                                         related_name='synergy_levels',
                                         blank=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f'{str(self.synergy.name)} [{self.level}]'

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']


class CharacterClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

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
        for profession in self.professions.all():
            for profile in profession.allowed_profiles.all():
                allowed_profiles.append(profile)
        return allowed_profiles

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Character class'
        verbose_name_plural = 'Character classes'


class CharacterProfession(models.Model):
    name = models.CharField(max_length=100, unique=True)
    character_class = models.ForeignKey(CharacterClass, related_name='professions', on_delete=models.PROTECT)
    description = models.TextField(max_length=4000, blank=True, null=True)
    start_perks = models.TextField(max_length=4000, blank=True, null=True)
    lvl_1 = models.CharField(max_length=500, blank=True, null=True)
    lvl_2 = models.CharField(max_length=500, blank=True, null=True)
    lvl_3 = models.CharField(max_length=500, blank=True, null=True)
    lvl_4 = models.CharField(max_length=500, blank=True, null=True)
    lvl_5 = models.CharField(max_length=500, blank=True, null=True)
    lvl_6 = models.CharField(max_length=500, blank=True, null=True)
    lvl_7 = models.CharField(max_length=500, blank=True, null=True)
    lvl_8 = models.CharField(max_length=500, blank=True, null=True)
    lvl_9 = models.CharField(max_length=500, blank=True, null=True)
    lvl_10 = models.CharField(max_length=500, blank=True, null=True)
    lvl_11 = models.CharField(max_length=500, blank=True, null=True)
    lvl_12 = models.CharField(max_length=500, blank=True, null=True)
    lvl_13 = models.CharField(max_length=500, blank=True, null=True)
    lvl_14 = models.CharField(max_length=500, blank=True, null=True)
    lvl_15 = models.CharField(max_length=500, blank=True, null=True)
    lvl_16 = models.CharField(max_length=500, blank=True, null=True)
    lvl_17 = models.CharField(max_length=500, blank=True, null=True)
    lvl_18 = models.CharField(max_length=500, blank=True, null=True)
    lvl_19 = models.CharField(max_length=500, blank=True, null=True)
    lvl_20 = models.CharField(max_length=500, blank=True, null=True)
    allowed_profiles = models.ManyToManyField(Profile, blank=True,
                                              limit_choices_to=
                                              Q(status='active_player') |
                                              Q(status='inactive_player') |
                                              Q(status='inactive_player') |
                                              Q(status='dead_player'),
                                              related_name='allowed_professions')
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

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


class EliteClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = models.ManyToManyField(to=Profile, blank=True,
                                              limit_choices_to=
                                              Q(status='active_player') |
                                              Q(status='inactive_player') |
                                              Q(status='dead_player'),
                                              related_name='allowed_elite_classes')
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

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
        verbose_name = 'Elite class'
        verbose_name_plural = 'Elite classes'


class EliteProfession(models.Model):
    name = models.CharField(max_length=100, unique=True)
    elite_class = models.ForeignKey(to=EliteClass, related_name='elite_professions', on_delete=models.PROTECT)
    description = models.TextField(max_length=4000, blank=True, null=True)
    start_perks = models.TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = models.ManyToManyField(to=Profile, blank=True,
                                              limit_choices_to=
                                              Q(status='active_player') |
                                              Q(status='inactive_player') |
                                              Q(status='dead_player'),
                                              related_name='allowed_elite_professions')
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

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


class WeaponClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

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
        verbose_name = 'Weapon class'
        verbose_name_plural = 'Weapon classes'


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


class WeaponType(models.Model):
    weapon_class = models.ForeignKey(to=WeaponClass, related_name='weapon_types', on_delete=models.PROTECT)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    pictures = models.ManyToManyField(to=Picture, related_name='weapon_pics', blank=True)

    delay = models.PositiveSmallIntegerField()
    damage_small_dices = models.CharField(max_length=10, blank=True, null=True)
    damage_small_add = models.PositiveSmallIntegerField(blank=True, null=True)
    damage_big_dices = models.CharField(max_length=10, blank=True, null=True)
    damage_big_add = models.PositiveSmallIntegerField(blank=True, null=True)
    damage_type = models.CharField(max_length=10, choices=DAMAGE_TYPES)
    special = models.TextField(max_length=4000, blank=True, null=True)
    range = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=5, choices=SIZES)
    trait = models.CharField(max_length=10, choices=TRAITS)
    avg_price_value = models.PositiveSmallIntegerField(blank=True, null=True)
    avg_price_currency = models.CharField(max_length=5, choices=CURRENCIES, blank=True, null=True)
    avg_weight = models.DecimalField(max_digits=10, decimal_places=1)

    allowed_profiles = models.ManyToManyField(to=Profile, blank=True,
                                              limit_choices_to=
                                              Q(status='active_player') |
                                              Q(status='inactive_player') |
                                              Q(status='dead_player'),
                                              related_name='allowed_weapon_types')
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

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


class PlateType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    pictures = models.ManyToManyField(to=Picture, related_name='plate_pics', blank=True)

    armor_class_bonus = models.PositiveSmallIntegerField(blank=True, null=True)
    parrying = models.PositiveSmallIntegerField(blank=True, null=True)
    endurance = models.PositiveSmallIntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=1)

    mod_max_agility = models.PositiveSmallIntegerField(blank=True, null=True)
    mod_max_movement = models.CharField(max_length=2, blank=True, null=True)

    mod_pickpocketing = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_lockpicking = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_sneaking_towns = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_sneaking_wilderness = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_hiding_towns = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_hiding_wilderness = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_climbing = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    mod_traps = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    allowed_profiles = models.ManyToManyField(to=Profile, blank=True,
                                              limit_choices_to=
                                              Q(status='active_player') |
                                              Q(status='inactive_player') |
                                              Q(status='dead_player'),
                                              related_name='allowed_plate_types')
    sorting_number = models.DecimalField(max_digits=3, decimal_places=2)

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


class ShieldType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    pictures = models.ManyToManyField(to=Picture, related_name='shield_pics', blank=True)

    enemies_no = models.PositiveSmallIntegerField()
    armor_class_bonus_close_combat = models.PositiveSmallIntegerField(blank=True, null=True)
    armor_class_bonus_distance_combat = models.PositiveSmallIntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=1)

    allowed_profiles = models.ManyToManyField(to=Profile, blank=True,
                                              limit_choices_to=
                                              Q(status='active_player') |
                                              Q(status='inactive_player') |
                                              Q(status='dead_player'),
                                              related_name='allowed_shield_types')
    sorting_number = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sorting_number']

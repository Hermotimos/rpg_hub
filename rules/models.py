from django.db import models
from django.db.models import Q
from users.models import Profile
from rpg_project.utils import create_sorting_name
from imaginarion.models import Picture


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Umiejętność')
    tested_trait = models.CharField(max_length=50, verbose_name='Cecha/Cechy')
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name='Opis')
    lvl_0 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_1 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_2 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_3 = models.TextField(max_length=4000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='site_features_pics')
    allowed_profiles = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='allowed_skills')
    sorting_name = models.CharField(max_length=101, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(Skill, self).save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    class Meta:
        ordering = ['sorting_name']


class Synergy(models.Model):
    name = models.CharField(max_length=100, verbose_name='Synergia')
    skills = models.ManyToManyField(Skill, related_name='skills')
    lvl_1 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_2 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_3 = models.TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='allowed_synergies',)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return ' + '.join(str(s) for s in self.skills.all())

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(Synergy, self).save(*args, **kwargs)

    def short_name(self):
        short_name = ''
        for char in str(self.name):
            if char in 'abcdefghijklmnopqrstuvwxyz':
                short_name += char
        return short_name

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Synergy'
        verbose_name_plural = 'Synergies'


class CharacterClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(CharacterClass, self).save(*args, **kwargs)

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
    allowed_profiles = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='allowed_professions')
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(CharacterProfession, self).save(*args, **kwargs)

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
    allowed_profiles = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='allowed_elite_classes')
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(EliteClass, self).save(*args, **kwargs)

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
    elite_class = models.ForeignKey(EliteClass, related_name='elite_professions', on_delete=models.PROTECT)
    description = models.TextField(max_length=4000, blank=True, null=True)
    start_perks = models.TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='allowed_elite_professions')
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(EliteProfession, self).save(*args, **kwargs)

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


class WeaponClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(WeaponClass, self).save(*args, **kwargs)

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
    weapon_class = models.ForeignKey(WeaponClass, related_name='weapon_types', on_delete=models.PROTECT)
    name = models.CharField(max_length=100, unique=True)
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
    avg_price_value = models.PositiveSmallIntegerField()
    avg_price_currency = models.CharField(max_length=5, choices=CURRENCIES)
    avg_weight = models.DecimalField(max_digits=10, decimal_places=1)

    description = models.TextField(max_length=4000, blank=True, null=True)
    pictures = models.ManyToManyField(Picture, related_name='weapons_pics', blank=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(WeaponType, self).save(*args, **kwargs)

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

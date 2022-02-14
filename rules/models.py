from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey as FK,
    ImageField,
    Manager,
    ManyToManyField as M2M,
    Model,
    PositiveSmallIntegerField,
    PROTECT,
    SmallIntegerField,
    TextField,
)
from django.db.models import Q

from imaginarion.models import PictureSet
from rpg_project.utils import create_sorting_name, rid_of_special_chars
from users.models import Profile


# =============================================================================


class Factor(Model):
    """Ex. KP, TRAF, OBR, IN, Życie, etc."""
    name = CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


PERCENTAGE_VALIDATOR = [MinValueValidator(0.01), MaxValueValidator(1.00)]
SIGN_CHOICES = [
    ('-', '-'),
    ('+', '+'),
]


class Modifier(Model):
    """Ex. factor and value combine into: +2 KP, -1 TRAF, +2 OBR, etc."""
    sign = CharField(max_length=1, choices=SIGN_CHOICES, default="+", blank=True, null=True)
    value_number = DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    value_percent = DecimalField(
        max_digits=3, decimal_places=2, validators=PERCENTAGE_VALIDATOR, blank=True, null=True)
    value_text = CharField(max_length=30, blank=True, null=True)
    factor = FK(to=Factor, related_name='modifiers', on_delete=PROTECT)
    overview = CharField(max_length=100)

    class Meta:
        ordering = ['factor', 'sign', 'value_number', 'value_percent', 'value_text']
        unique_together = [
            ('factor', 'sign', 'value_number'),
            ('factor', 'sign', 'value_percent'),
            ('factor', 'sign', 'value_text'),
        ]

    def __str__(self):
        return str(self.overview)

    def create_overview(self):
        value = ""
        if self.value_number:
            value = str(self.value_number).rstrip('0').rstrip('.')
        elif self.value_percent:
            value = str(float(self.value_percent) * 100).rstrip('0').rstrip('.') + "%"
        elif self.value_text:
            value = self.value_text
        return f"{self.sign}{value} {self.factor.name}"
        
    def save(self, *args, **kwargs):
        self.overview = self.create_overview()
        super().save(*args, **kwargs)


class RulesComment(Model):
    text = TextField()

    class Meta:
        ordering = ['text']

    def __str__(self):
        return self.text
        
        
class Condition(Model):
    """A model for specifying Modifier usage conditions."""
    text = CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['text']

    def __str__(self):
        return self.text


class CombatType(Model):
    """A model to store info about the kind of combat a Modifier applies to."""
    name = CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ConditionalModifier(Model):
    modifier = FK(to=Modifier, related_name="conditional_modifiers", on_delete=CASCADE)
    conditions = M2M(to=Condition, related_name="conditional_modifiers", blank=True)
    combat_types = M2M(to=CombatType, related_name="conditional_modifiers", blank=True)
    overview = CharField(max_length=100)

    class Meta:
        ordering = ['modifier']

    def __str__(self):
        return str(self.overview)

    def create_overview(self):
        conditions = ""
        if self.conditions.exists():
            conditions = f" [{' | '.join([str(condition) for condition in self.conditions.all()])}]"
        return f"{self.modifier}{conditions}"

    def save(self, *args, **kwargs):
        self.overview = self.create_overview()
        super().save(*args, **kwargs)


class Perk(Model):
    """A class describing a special ability of an item or a skill level."""
    name = CharField(max_length=50, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    conditional_modifiers = M2M(to=ConditionalModifier, related_name='perks', blank=True)
    cost = CharField(max_length=200, blank=True, null=True)
    comments = M2M(to=RulesComment, related_name='perks', blank=True)

    class Meta:
        ordering = ['name', 'description']

    def __str__(self):
        return self.name


# =============================================================================


class SkillKind(Model):
    """A classification category for Skills."""
    name = CharField(max_length=100, unique=True)
    sorting_name = CharField(max_length=101, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
        
class SkillType(Model):
    """A classification category for Skills."""
    kinds = M2M(to=SkillKind, related_name='skill_types', blank=True)
    name = CharField(max_length=100, unique=True)
    sorting_name = CharField(max_length=101, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        kinds = "|".join([str(kind) for kind in self.kinds.all()])
        return f"[{kinds}] {self.name}"
      
        
class SkillGroup(Model):
    """A loose grouping category for Skills."""
    name = CharField(max_length=100, unique=True)
    type = FK(to=SkillType, related_name='skill_groups', on_delete=PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Skill(Model):
    name = CharField(max_length=100, unique=True)
    tested_trait = CharField(max_length=50, blank=True, null=True)
    image = ImageField(upload_to='site_features_pics', blank=True, null=True)
    group = FK(to=SkillGroup, related_name='skills', on_delete=PROTECT, blank=True, null=True)
    types = M2M(to=SkillType, related_name='skills', blank=True)
    allowed_profiles = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_skills',
        blank=True,
    )
    sorting_name = CharField(max_length=101, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        return rid_of_special_chars(self.name)


S_LEVELS = [
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3')
]


class SkillLevel(Model):
    skill = FK(to=Skill, related_name='skill_levels', on_delete=CASCADE)
    level = CharField(max_length=10, choices=S_LEVELS)
    description = TextField(max_length=4000, blank=True, null=True)
    perks = M2M(to=Perk, related_name='skill_levels', blank=True)
    acquired_by = M2M(to=Profile, related_name='skill_levels', blank=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name', 'id']

    def __str__(self):
        return f'{str(self.skill.name)} [{self.level}]'

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)


class TheologySkillManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(name__icontains='Doktryn')
                       | Q(name__icontains='Kult')
                       | Q(name__icontains='Mister')
                       | Q(name__icontains='Wierzenia')
                       | Q(name__icontains='Wiar')
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
    name = CharField(max_length=100)
    skills = M2M(to=Skill, related_name='skills')
    allowed_profiles = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_synergies',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Synergy'
        verbose_name_plural = 'Synergies'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        return rid_of_special_chars(self.name)


class SynergyLevel(Model):
    synergy = FK(to=Synergy, related_name='synergy_levels', on_delete=CASCADE)
    level = CharField(max_length=10, choices=S_LEVELS[1:])
    description = TextField(max_length=4000, blank=True, null=True)
    perks = M2M(to=Perk, related_name='synergy_levels', blank=True)
    acquired_by = M2M(to=Profile, related_name='synergy_levels', blank=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        
    def __str__(self):
        return f'{str(self.synergy.name)} [{self.level}]'

    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)


# =============================================================================


class Profession(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Profession'
        verbose_name_plural = 'Professions'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        return rid_of_special_chars(self.name)

    def allowed_list(self):
        allowed_profiles = []
        for klass in self.klasses.all():
            for profile in klass.allowed_profiles.all():
                allowed_profiles.append(profile)
        return allowed_profiles


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
    allowed_profiles = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_klasses',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Klass'
        verbose_name_plural = 'Klasses'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        return rid_of_special_chars(self.name)


class EliteProfession(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_elite_classes',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Elite profession'
        verbose_name_plural = 'Elite professions'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        return rid_of_special_chars(self.name)


class EliteKlass(Model):
    name = CharField(max_length=100, unique=True)
    elite_profession = FK(
        to=EliteProfession,
        related_name='elite_klasses',
        on_delete=PROTECT,
    )
    description = TextField(max_length=4000, blank=True, null=True)
    start_perks = TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_elite_klasses',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Elite klass'
        verbose_name_plural = 'Elite klasses'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        return rid_of_special_chars(self.name)


# =============================================================================


class WeaponType(Model):
    name = CharField(max_length=100, unique=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        verbose_name = 'Weapon type'
        verbose_name_plural = 'Weapon types'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        return rid_of_special_chars(self.name)


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
    # modifiers = M2M(to=ConditionalModifier, related_name='weapons', blank=True)
    picture_sets = M2M(to=PictureSet, related_name='weapons', blank=True)
    
    # -------------------# TODO marked for removal [in 2023]-------------------
    delay = PositiveSmallIntegerField()
    damage_big_dices = CharField(max_length=10, blank=True, null=True)
    damage_big_add = PositiveSmallIntegerField(blank=True, null=True)
    # -------------------------------------------------------------------------
    
    damage_small_dices = CharField(max_length=10, blank=True, null=True)
    damage_small_add = PositiveSmallIntegerField(blank=True, null=True)
    damage_type = CharField(max_length=10, choices=DAMAGE_TYPES)
    special = TextField(max_length=4000, blank=True, null=True)
    range = CharField(max_length=100, blank=True, null=True)
    size = CharField(max_length=5, choices=SIZES)
    trait = CharField(max_length=10, choices=TRAITS)
    avg_price_value = PositiveSmallIntegerField(blank=True, null=True)
    avg_price_currency = CharField(max_length=5, choices=CURRENCIES, blank=True, null=True)
    avg_weight = DecimalField(max_digits=10, decimal_places=1)
    allowed_profiles = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_weapons',
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def short_name(self):
        return rid_of_special_chars(self.name)

    def damage_summary(self):
        damage_small = str(self.damage_small_dices)
        # if self.damage_small_add:
        #     damage_small += ('+' + str(self.damage_small_add))
        # damage_big = str(self.damage_big_dices)
        # if self.damage_big_add:
        #     damage_big += ('+' + str(self.damage_big_add))
        damage_small_add = ""
        if self.damage_small_add:
            damage_small_add += ("+" + str(self.damage_small_add))
        return f"{self.damage_small_dices}{damage_small_add}"


# =============================================================================


class Plate(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    picture_sets = M2M(to=PictureSet, related_name='plates', blank=True)
    
    armor_class_bonus = PositiveSmallIntegerField(blank=True, null=True)
    parrying = PositiveSmallIntegerField(blank=True, null=True)
    endurance = PositiveSmallIntegerField()
    weight = DecimalField(max_digits=10, decimal_places=1)
    comment = TextField(max_length=200, blank=True, null=True)
    mod_running = SmallIntegerField(blank=True, null=True)
    mod_swimming = SmallIntegerField(blank=True, null=True)
    mod_climbing = SmallIntegerField(blank=True, null=True)
    mod_listening = SmallIntegerField(blank=True, null=True)
    mod_lookout = SmallIntegerField(blank=True, null=True)
    mod_trailing = SmallIntegerField(blank=True, null=True)
    mod_sneaking = SmallIntegerField(blank=True, null=True)
    mod_hiding = SmallIntegerField(blank=True, null=True)
    mod_traps = SmallIntegerField(blank=True, null=True)
    mod_lockpicking = SmallIntegerField(blank=True, null=True)
    mod_pickpocketing = SmallIntegerField(blank=True, null=True)
    mod_conning = SmallIntegerField(blank=True, null=True)
    
    allowed_profiles = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_plates',
        blank=True,
    )
    sorting_number = DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        ordering = ['sorting_number']

    def __str__(self):
        return self.name

    def short_name(self):
        return rid_of_special_chars(self.name)


class Shield(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    armor_class_bonus = PositiveSmallIntegerField()
    weight = DecimalField(max_digits=10, decimal_places=1)
    comment = TextField(max_length=200, blank=True, null=True)
    picture_set = FK(
        to=PictureSet,
        related_name='shields',
        blank=True,
        null=True,
        on_delete=PROTECT)
    allowed_profiles = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_shields',
        blank=True,
    )
    sorting_number = DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        ordering = ['sorting_number']
        
    def __str__(self):
        return self.name

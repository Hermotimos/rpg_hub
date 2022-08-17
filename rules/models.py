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
    OneToOneField as One2One,
    PositiveSmallIntegerField,
    PROTECT,
    Q,
    SmallIntegerField,
    TextField,
)

from imaginarion.models import PictureSet
from users.models import Profile


# =============================================================================


class Factor(Model):
    """Ex. KP, TRAF, OBR, IN, Życie, etc."""
    name = CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


PERCENTAGE_VALIDATOR = [
    MinValueValidator(0.01),
    MaxValueValidator(1.00),
]
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

    class Meta:
        ordering = ['factor', 'sign', 'value_number', 'value_percent', 'value_text']
        unique_together = [
            ('factor', 'sign', 'value_number'),
            ('factor', 'sign', 'value_percent'),
            ('factor', 'sign', 'value_text'),
        ]

    def __str__(self):
        value = ""
        if self.value_number:
            value = str(self.value_number).rstrip('0').rstrip('.')
        elif self.value_percent:
            value = str(float(self.value_percent) * 100).rstrip('0').rstrip('.') + "%"
        elif self.value_text:
            value = self.value_text
        return f"{self.sign}{value} {self.factor.name}"


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

    class Meta:
        ordering = ['modifier']

    def __str__(self):
        conditions = ""
        if self.conditions.exists():
            conditions = f" [{' | '.join([str(condition) for condition in self.conditions.all()])}]"
        combat_types = [str(ct).split()[-1][:4] for ct in self.combat_types.all()]
        combat_types = "".join(["/" + str(ct) for ct in combat_types])
        return f"{self.modifier}{conditions} {combat_types}"

        
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


# class ItemType(Model):
#     name = CharField(max_length=100, unique=True)
#     description = TextField(max_length=4000, blank=True, null=True)
#     picture_set = FK(
#         to=PictureSet,
#         related_name='item_types',
#         blank=True,
#         null=True,
#         on_delete=PROTECT)
#     allowees = M2M(
#         to=Profile,
#         limit_choices_to=Q(status='player'),
#         related_name='allowed_item_types',
#         blank=True)
#     weight = DecimalField(max_digits=10, decimal_places=1)
#     price = CharField(max_length=20)
#
#     class Meta:
#         ordering = ['name']
#
#     def __str__(self):
#         return self.name


class Plate(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    picture_set = FK(
        to=PictureSet,
        related_name='plates',
        blank=True,
        null=True,
        on_delete=PROTECT)
    allowees = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_plates',
        blank=True)
    
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
    
    sorting_number = DecimalField(max_digits=3, decimal_places=2)
    
    class Meta:
        ordering = ['sorting_number']
    
    def __str__(self):
        return self.name


class Shield(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    picture_set = FK(
        to=PictureSet,
        related_name='shields',
        blank=True,
        null=True,
        on_delete=PROTECT)
    allowees = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_shields',
        blank=True)
    armor_class_bonus = PositiveSmallIntegerField()
    weight = DecimalField(max_digits=10, decimal_places=1)
    comment = TextField(max_length=200, blank=True, null=True)
    sorting_number = DecimalField(max_digits=3, decimal_places=2)
    
    class Meta:
        ordering = ['sorting_number']
    
    def __str__(self):
        return self.name


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


class DamageType(Model):
    description = CharField(max_length=30, blank=True, null=True)
    type = CharField(max_length=10, choices=DAMAGE_TYPES)
    damage = CharField(max_length=15)
    special = CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['type', 'description']
        unique_together = [('description', 'type', 'damage', 'special')]

    def __str__(self):
        description = f" {self.description}" if self.description else ""
        special = f" {self.special}" if self.special else ""
        return f"{self.damage} [{self.type}]{description}{special}"
    
    @property
    def short(self):
        description = f" {self.description}" if self.description else ""
        return f"{self.damage} [{self.type}]{description}"


class WeaponType(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(max_length=4000, blank=True, null=True)
    picture_set = FK(
        to=PictureSet,
        related_name='weapon_types',
        blank=True,
        null=True,
        on_delete=PROTECT)
    damage_types = M2M(to=DamageType, related_name='weapon_types')
    comparables = M2M(to='self', symmetrical=False, blank=True)
    size = CharField(max_length=5, choices=SIZES)
    trait = CharField(max_length=10, choices=TRAITS)
    avg_price_value = PositiveSmallIntegerField(blank=True, null=True)
    avg_price_currency = CharField(
        max_length=5, choices=CURRENCIES,  blank=True, null=True)
    avg_weight = DecimalField(max_digits=10, decimal_places=1)
    allowees = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_weapon_types',
        blank=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# =============================================================================


class SkillKind(Model):
    """A classification category for Skills."""
    name = CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
        
class SkillType(Model):
    """A classification category for Skills."""
    name = CharField(max_length=100, unique=True)
    kinds = M2M(to=SkillKind, related_name='skill_types', blank=True)

    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name

        
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
    name_second = CharField(max_length=100, blank=True, null=True)
    name_origin = CharField(max_length=100, blank=True, null=True)
    tested_trait = CharField(max_length=50, blank=True, null=True)
    image = ImageField(upload_to='skills', blank=True, null=True)
    group = FK(to=SkillGroup, related_name='skills', on_delete=PROTECT, blank=True, null=True)
    types = M2M(to=SkillType, related_name='skills', blank=True)
    allowees = M2M(
        to=Profile,
        limit_choices_to=Q(status='player'),
        related_name='allowed_skills',
        blank=True)
    # ------------------------------------------
    # For RegularSkills for weapon masteries
    weapon = One2One(to=WeaponType, on_delete=CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

       
class RegularSkillManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(types__kinds__name="Powszechne")
        return qs.distinct()


class RegularSkill(Skill):
    objects = RegularSkillManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill - POWSZECHNE'
        verbose_name_plural = 'Skills - POWSZECHNE'
        
        
class MentalSkillManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(types__kinds__name="Mentalne")
        return qs.distinct()


class MentalSkill(Skill):
    objects = MentalSkillManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill - MENTALNE'
        verbose_name_plural = 'Skills - MENTALNE'
        
        
class PriestsSkillManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(types__kinds__name="Moce Kapłańskie")
        qs = qs.prefetch_related('types__kinds')
        return qs.distinct()


class PriestsSkill(Skill):
    objects = PriestsSkillManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill - MOCE KAPŁAŃSKIE'
        verbose_name_plural = 'Skills - MOCE KAPŁAŃSKIE'
        

class SorcerersSkillManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(types__kinds__name="Zaklęcia")
        return qs.distinct()


class SorcerersSkill(Skill):
    objects = SorcerersSkillManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill - ZAKLĘCIA'
        verbose_name_plural = 'Skills - ZAKLĘCIA'
       
        
class TheurgistsSkillManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(types__kinds__name="Moce Teurgiczne")
        return qs.distinct()


class TheurgistsSkill(Skill):
    objects = TheurgistsSkillManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill - MOCE TEURGICZNE'
        verbose_name_plural = 'Skills - MOCE TEURGICZNE'
        

# -----------------------------------------------------------------------------


class SkillLevel(Model):
    LEVELS = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    ]
    TRAITS = [
        ('Sił', 'Sił'),
        ('Zrc', 'Zrc'),
        ('Kon', 'Kon'),
        ('Sił/Zrc', 'Sił/Zrc'),
        ('Sił/Kon', 'Sił/Kon'),
        ('Zrc/Kon', 'Zrc/Kon'),
        ('Sił/Zrc/Kon', 'Sił/Zrc/Kon'),
    ]
    
    skill = FK(to=Skill, related_name='skill_levels', on_delete=CASCADE)
    level = CharField(max_length=10, choices=LEVELS)
    description = TextField(blank=True, null=True)
    perks = M2M(to=Perk, related_name='skill_levels', blank=True)
    # ------------------------------------------
    distance = PositiveSmallIntegerField(blank=True, null=True)
    radius = PositiveSmallIntegerField(blank=True, null=True)
    duration = PositiveSmallIntegerField(blank=True, null=True)
    damage = CharField(max_length=20, blank=True, null=True)
    saving_throw_malus = PositiveSmallIntegerField(blank=True, null=True)
    saving_throw_trait = CharField(
        max_length=20, choices=TRAITS, blank=True, null=True)

    class Meta:
        ordering = ['skill__name', 'level']

    def __str__(self):
        return f'{str(self.skill.name)} [{self.level}]'


class RegularSkillLevelManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(skill__in=RegularSkill.objects.all())
        return qs.distinct()


class RegularSkillLevel(SkillLevel):
    objects = RegularSkillLevelManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill Level - POWSZECHNE'
        verbose_name_plural = 'Skill Levels - POWSZECHNE'
        

class MentalSkillLevelManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(skill__in=MentalSkill.objects.all())
        return qs.distinct()


class MentalSkillLevel(SkillLevel):
    objects = MentalSkillLevelManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill Level - MENTALNE'
        verbose_name_plural = 'Skill Levels - MENTALNE'
        

class PriestsSkillLevelManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(skill__in=PriestsSkill.objects.all())
        return qs.distinct()


class PriestsSkillLevel(SkillLevel):
    objects = PriestsSkillLevelManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill Level - MOCE KAPŁAŃSKIE'
        verbose_name_plural = 'Skill Levels - MOCE KAPŁAŃSKIE'
        

class SorcerersSkillLevelManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(skill__in=SorcerersSkill.objects.all())
        return qs.distinct()


class SorcerersSkillLevel(SkillLevel):
    objects = SorcerersSkillLevelManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill Level - ZAKLĘCIA'
        verbose_name_plural = 'Skill Levels - ZAKLĘCIA'
        

class TheurgistsSkillLevelManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(skill__in=TheurgistsSkill.objects.all())
        return qs.distinct()


class TheurgistsSkillLevel(SkillLevel):
    objects = TheurgistsSkillLevelManager()

    class Meta:
        proxy = True
        verbose_name = 'Skill Level - MOCE TEURGICZNE'
        verbose_name_plural = 'Skill Levels - MOCE TEURGICZNE'
        

# -----------------------------------------------------------------------------


class Synergy(Model):
    name = CharField(max_length=100)
    skills = M2M(to=Skill, related_name='skills')

    class Meta:
        ordering = ['name']
        verbose_name = 'Synergy'
        verbose_name_plural = 'Synergies'

    def __str__(self):
        return self.name


class RegularSynergyManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(skills__types__kinds__name__in=["Mentalne"])
        return qs.distinct()


class RegularSynergy(Synergy):
    objects = RegularSynergyManager()

    class Meta:
        proxy = True
        verbose_name = 'Synergy - POWSZECHNE'
        verbose_name_plural = 'Synergies - POWSZECHNE'


class MentalSynergyManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(skills__types__kinds__name="Mentalne")
        return qs.distinct()


class MentalSynergy(Synergy):
    objects = MentalSynergyManager()

    class Meta:
        proxy = True
        verbose_name = 'Synergy - MENTALNE'
        verbose_name_plural = 'Synergies - MENTALNE'


# -----------------------------------------------------------------------------


class SynergyLevel(Model):
    LEVELS = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    ]
    synergy = FK(to=Synergy, related_name='synergy_levels', on_delete=CASCADE)
    level = CharField(max_length=10, choices=LEVELS)
    description = TextField(max_length=4000, blank=True, null=True)
    perks = M2M(to=Perk, related_name='synergy_levels', blank=True)
    skill_levels = M2M(to=SkillLevel, related_name='synergy_levels')

    class Meta:
        ordering = ['synergy', 'level']
        
    def __str__(self):
        return f'{str(self.synergy.name)} [{self.level}]'


class RegularSynergyLevelManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(synergy__in=MentalSynergy.objects.all())
        return qs.distinct()


class RegularSynergyLevel(SynergyLevel):
    objects = RegularSynergyLevelManager()

    class Meta:
        proxy = True
        verbose_name = 'Synergy Level - POWSZECHNE'
        verbose_name_plural = 'Synergy Levels - POWSZECHNE'


class MentalSynergyLevelManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(synergy__in=MentalSynergy.objects.all())
        return qs.distinct()


class MentalSynergyLevel(SynergyLevel):
    objects = MentalSynergyLevelManager()

    class Meta:
        proxy = True
        verbose_name = 'Synergy Level - MENTALNE'
        verbose_name_plural = 'Synergy Levels - MENTALNE'


# =============================================================================


class Profession(Model):
    TYPES = [
        ('Pospolite', 'Pospolite'),
        ('Elitarne', 'Elitarne'),
        ('Hermetyczne', 'Hermetyczne'),
    ]
    
    name = CharField(max_length=100, unique=True)
    type = CharField(max_length=50, choices=TYPES)
    description = TextField(max_length=4000, blank=True, null=True)
    allowees = M2M(to=Profile, related_name='professions_allowed', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Profession'
        verbose_name_plural = '--- PROFESSIONS'

    def __str__(self):
        return self.name


class SubProfession(Model):
    name = CharField(max_length=100, unique=True)
    profession = FK(
        to=Profession, related_name='subprofessions', on_delete=PROTECT)
    description = TextField(max_length=4000, blank=True, null=True)
    essential_skills = M2M(to=Skill, blank=True)
    allowees = M2M(to=Profile, related_name='subprofessions_allowed', blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'SubProfession'
        verbose_name_plural = '--- SUBPROFESSIONS'

    def __str__(self):
        return self.name


class Sphragis(Model):
    name = CharField(max_length=100, unique=True)
    name_genitive = CharField(max_length=100, unique=True)
    color = CharField(max_length=7, default='#000000')
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

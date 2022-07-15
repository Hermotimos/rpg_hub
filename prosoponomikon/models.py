from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    F,
    ForeignKey as FK,
    Manager,
    ManyToManyField as M2M,
    Model,
    OneToOneField as One2One,
    PositiveSmallIntegerField,
    Prefetch,
    PROTECT,
    TextField,
)
from django.db.models.functions import Substr, Lower
from django.db.models.signals import post_save

from knowledge.models import BiographyPacket, DialoguePacket
from rules.models import SubProfession, Skill, SkillLevel, WeaponType, Sphragis, SkillType
from toponomikon.models import Location
from users.models import Profile


class FirstNameGroup(Model):
    NAME_GROUP_TYPES = (
        ('local', 'local'),
        ('racial', 'racial'),
        ('social', 'social'),
    )
    title = CharField(max_length=250, unique=True)
    type = CharField(max_length=50, choices=NAME_GROUP_TYPES)
    description = TextField(blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


NAME_TYPES = (
    ('MALE', 'MALE'),
    ('FEMALE', 'FEMALE'),
    ('UNISEX', 'UNISEX'),
)


class AffixGroupManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('name_group')
        return qs


class AffixGroup(Model):
    objects = AffixGroupManager()
    
    affix = CharField(max_length=100)
    type = CharField(max_length=20, choices=NAME_TYPES, default='MALE')
    name_group = FK(to=FirstNameGroup, related_name='affix_groups', on_delete=PROTECT)
    
    class Meta:
        ordering = ['name_group', 'type', 'affix']
        unique_together = ('affix', 'type', 'name_group')
        
    def __str__(self):
        return f"[{self.name_group}] | {self.type} | {self.affix}"
    

class AuxiliaryNameGroupManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('location')
        return qs


class AuxiliaryNameGroup(Model):
    """A class for storing info about social or local specifics of a name.
    This may serve to differentiate names within a "big" location indicated in
    name.affix_group.name_group, ex.
        1)
        name_group ~ Fehzan,
        auxiliary_name_group ~ social_group='Royal names' or location='Ketra'
        2)
        name_group ~ Altankara | Nowa Altankara | Bastos | Skadia,
        auxiliary_name_group ~ location='Skadia'
    The 'color' attribute is intended to help distinguish these visually within
    a NameGroup on site.
    """
    objects = AuxiliaryNameGroupManager()

    color = CharField(max_length=100, blank=True, null=True)
    location = FK(to=Location, blank=True, null=True, on_delete=PROTECT)
    social_info = TextField(
        help_text='Social group indication if no location',
        blank=True,
        null=True)

    class Meta:
        ordering = ['social_info', 'location']

    def __str__(self):
        return f"{self.location or self.social_info}"


class FirstNameManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('affix_group', 'auxiliary_group')
        return qs
    
    
class FirstName(Model):
    objects = FirstNameManager()
    
    form = CharField(max_length=50, unique=True)
    form_2 = CharField(max_length=50, blank=True, null=True)
    info = TextField(blank=True, null=True)
    is_ancient = BooleanField(default=False)
    # FK fields nullable to allow creation of Character via registration form
    affix_group = FK(
        to=AffixGroup,
        related_name='first_names',
        on_delete=PROTECT,
        blank=True, null=True)
    auxiliary_group = FK(
        to=AuxiliaryNameGroup, on_delete=PROTECT, blank=True, null=True)
    
    class Meta:
        ordering = ['auxiliary_group', 'form']

    def __str__(self):
        return self.form


# -----------------------------------------------------------------------------


class FamilyNameGroup(Model):
    title = CharField(max_length=250, unique=True)
    description = TextField(blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
    
    
class FamilyName(Model):
    form = CharField(max_length=50, unique=True)
    info = TextField(blank=True, null=True)
    locations = M2M(to=Location, related_name="family_names", blank=True)
    group = FK(to=FamilyNameGroup, on_delete=PROTECT)

    class Meta:
        ordering = ['group', 'form']
    
    def __str__(self):
        return self.form


# -----------------------------------------------------------------------------


class CharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(profile__status='spectator')
        qs = qs.select_related('first_name', 'family_name', 'profile')
        return qs
    
    
class Character(Model):
    objects = CharacterManager()
    
    profile = One2One(to=Profile, on_delete=CASCADE)
    first_name = FK(
        to=FirstName, related_name='characters', on_delete=PROTECT,
        blank=True, null=True)
    family_name = FK(
        to=FamilyName, related_name='characters', on_delete=PROTECT,
        blank=True, null=True)
    cognomen = CharField(max_length=50, blank=True, null=True)
    fullname = CharField(max_length=150)
    
    strength = PositiveSmallIntegerField(blank=True, null=True)
    dexterity = PositiveSmallIntegerField(blank=True, null=True)
    endurance = PositiveSmallIntegerField(blank=True, null=True)
    experience = PositiveSmallIntegerField(blank=True, null=True)

    description = TextField(blank=True, null=True)
    frequented_locations = M2M(to=Location, related_name='characters', blank=True)
    biography_packets = M2M(to=BiographyPacket, related_name='characters', blank=True)
    dialogue_packets = M2M(to=DialoguePacket, related_name='characters', blank=True)
    subprofessions = M2M(to=SubProfession, related_name='characters', blank=True)
    acquaintances = M2M(
        to='self', through='Acquaintanceship', related_name='acquaintaned_to',
        blank=True, symmetrical=False)
    skill_levels = M2M(
        to=SkillLevel,
        through='Acquisition',
        related_name='acquiring_characters',
        blank=True)
    
    class Meta:
        ordering = ['fullname']
        verbose_name = '*Character'
        verbose_name_plural = '*Characters (ALL)'
    
    def __str__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        first_name = f"{self.first_name} " if self.first_name else ""
        family_name = f"{self.family_name} " if self.family_name else ""
        cognomen = f"{self.cognomen} " if self.cognomen else ""
        self.fullname = f"{first_name}{family_name}{cognomen}".strip()
        super().save(*args, **kwargs)
    
    def informables(self):
        qs = Profile.active_players.select_related('character')
        qs = qs.exclude(character__in=self.acquaintaned_to.all())
        qs = qs.exclude(character=self)
        return qs
        
    def acquaintanceships(self):
        return Acquaintanceship.objects.filter(
            knowing_character=self
        ).select_related(
            'known_character__profile',
        ).annotate(
            initial=Lower(Substr('known_character__fullname', 1, 1)))

    def acquisitions_for_character_sheet(self):
        acquisitions = self.acquisitions.annotate(
            type=F('skill_level__skill__types__name'),
            group=F('skill_level__skill__group__name'),
        ).prefetch_related(
            'skill_level__skill',
            'skill_level__perks__conditional_modifiers__conditions',
            'skill_level__perks__conditional_modifiers__combat_types',
            'skill_level__perks__conditional_modifiers__modifier__factor',
            'skill_level__perks__comments',
            'weapon',
            'sphragis',
        ).order_by(
            # order_by combined with distinct for "DISTINCT ON" query:
            # https://docs.djangoproject.com/en/4.0/ref/models/querysets/#distinct
            'skill_level__skill__name',
            'weapon__name',
            'sphragis__name',
            '-skill_level__level'
        ).distinct(
            'skill_level__skill__name',
            'weapon__name',
            'sphragis__name'
        )
        return acquisitions
        
    def skill_types_for_character_sheet(self):
        skills = Skill.objects.filter(
            skill_levels__acquiring_characters=self
        ).prefetch_related(
            'skill_levels__perks__conditional_modifiers__conditions',
            'skill_levels__perks__conditional_modifiers__combat_types',
            'skill_levels__perks__conditional_modifiers__modifier__factor',
            'skill_levels__perks__comments',
        ).select_related(
            'group__type'
        ).distinct()

        skill_types = SkillType.objects.filter(
            skills__in=skills
        ).prefetch_related(
            Prefetch('skills', queryset=skills),
            'skill_groups',
        ).distinct()
        
        return skill_types
    
        
class CharacterAcquaintanceships(Character):
    """A class to enable a separate AdminModel-s."""
    
    class Meta:
        proxy = True
        verbose_name = '*Character (ACQUAINTANCESHIPS)'
        verbose_name_plural = '*Characters (ACQUAINTANCESHIPS)'

        
class CharacterAcquisitions(Character):
    """A class to enable a separate AdminModel-s."""
    
    class Meta:
        proxy = True
        verbose_name = '*Character (ACQUISITIONS)'
        verbose_name_plural = '*Characters (ACQUISITIONS)'

        
class PlayerCharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(profile__status='player')
        return qs


class PlayerCharacter(Character):
    objects = PlayerCharacterManager()
    
    class Meta:
        proxy = True
        verbose_name = '- Player'
        verbose_name_plural = '- Players'


class NPCCharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(profile__status='npc')
        return qs


class NPCCharacter(Character):
    objects = NPCCharacterManager()
    
    class Meta:
        proxy = True
        verbose_name = '- NPC'
        verbose_name_plural = '- NPCs'


class NonGMCharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(profile__status='gm')
        return qs


class NonGMCharacter(Character):
    objects = NonGMCharacterManager()
    
    class Meta:
        proxy = True
        verbose_name = '--- Player or NPC'
        verbose_name_plural = '--- Players and NPCs'


# -----------------------------------------------------------------------------


class Acquaintanceship(Model):
    knowing_character = FK(to=Character, related_name='known_characters', on_delete=CASCADE)
    known_character = FK(to=Character, related_name='knowing_characters', on_delete=CASCADE)
    is_direct = BooleanField(default=False)
    knows_if_dead = BooleanField(default=False)

    class Meta:
        ordering = ['known_character']
        unique_together = ['known_character', 'knowing_character']

    def __str__(self):
        return f"{self.knowing_character} -> {self.known_character}"


# -----------------------------------------------------------------------------


class Acquisition(Model):
    character = FK(to=Character, related_name='acquisitions', on_delete=CASCADE)
    skill_level = FK(to=SkillLevel, related_name='acquisitions', on_delete=CASCADE)
    weapon = FK(to=WeaponType, on_delete=CASCADE, blank=True, null=True)
    sphragis = FK(to=Sphragis, on_delete=CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['character', 'skill_level__skill', 'skill_level']
        unique_together = [
            ['character', 'skill_level', 'weapon'],
            ['character', 'skill_level', 'sphragis'],
        ]

    def __str__(self):
        weapon = f" {self.weapon}" if self.weapon else ""
        sphragis = f" ({self.sphragis})" if self.sphragis else ""
        return f"{self.character}: {self.skill_level}{weapon}{sphragis}"


# -----------------------------------------------------------------------------


def update_acquaintanceships(sender, instance, created, **kwargs):
    """Make an Acquaintance for GMs -> new Character."""
    if created:
        for gm_character in Character.objects.filter(profile__status='gm'):
            Acquaintanceship.objects.create(
                knowing_character=gm_character,
                known_character=instance,
                is_direct=True,
                knows_if_dead=True)


post_save.connect(
    receiver=update_acquaintanceships,
    sender=Character)

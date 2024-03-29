from django.conf import settings
from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    F, ForeignKey as FK,
    ImageField,
    Manager,
    ManyToManyField as M2M,
    Model,
    OneToOneField as One2One,
    Q,
    PositiveSmallIntegerField,
    Prefetch,
    PROTECT,
    TextField,
    Value,
)
from django.db.models.functions import Substr, Lower, Coalesce, Replace
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from knowledge.models import BiographyPacket, DialoguePacket
from rpg_project.utils import OrderByPolish, clear_cache, profiles_to_userids
from rules.models import SubProfession, Skill, SkillLevel, WeaponType, \
    SkillType, Spell, Domain, Sphere
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
        ordering = [OrderByPolish('social_info'), OrderByPolish('location__name')]

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
    # FK fields nullable to allow creation of Character via registration form
    affix_group = FK(
        to=AffixGroup,
        related_name='first_names',
        on_delete=PROTECT,
        blank=True, null=True)
    auxiliary_group = FK(
        to=AuxiliaryNameGroup, on_delete=PROTECT, blank=True, null=True)
    isarchaic = BooleanField(default=False)
    origin = FK(
        "self", related_name='originatedfirstnames',
        null=True, blank=True, on_delete=PROTECT)
    equivalents = M2M('self', symmetrical=True, blank=True)
    meaning = TextField(max_length=10000, blank=True, null=True)
    comments = TextField(max_length=10000, blank=True, null=True)

    class Meta:
        ordering = [
            OrderByPolish('auxiliary_group__social_info'),
            OrderByPolish('auxiliary_group__location__name'),
            'form']

    def __str__(self):
        return self.form

    def save(self, *args, **kwargs):
        """Save Character-s on their FirstName update."""
        super().save(*args, **kwargs)
        for character in self.characters.all():
            character.save()


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

    def save(self, *args, **kwargs):
        """Save Character-s on their FamilyName update."""
        super().save(*args, **kwargs)
        for character in self.characters.all():
            character.save()

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
    power = PositiveSmallIntegerField(blank=True, null=True)
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
    spells = M2M(
        to=Spell,
        through='SpellAcquisition',
        related_name='acquiring_characters',
        blank=True)
    # -------------------------------------------------------------------------
    created_by = FK(
        to=Profile, related_name='characters_created', on_delete=CASCADE,
        blank=True, null=True)

    class Meta:
        ordering = [OrderByPolish('fullname')]
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

        from items.models import ItemCollection
        if not ItemCollection.objects.filter(owner=self):
            ItemCollection.objects.create(owner=self, name="Osobisty")

        for character in Character.objects.filter(profile__status__in=['gm', 'spectator']):
            if not Acquaintanceship.objects.filter(knowing_character=character, known_character=self,).exists():
                Acquaintanceship.objects.create(
                    knowing_character=character,
                    known_character=self,
                    is_direct=True,
                    knows_if_dead=True)

    def get_absolute_url(self):
        return settings.BASE_URL + reverse('prosoponomikon:character', kwargs={'character_id' : self.id})

    def informables(self, current_profile):
        qs = current_profile.character.acquaintanceships()
        qs = qs.exclude(
            known_character__in=self.acquaintaned_to.all()
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

    def acquaintanceships(self):
        qs = self.known_characters.select_related(
            'known_character__profile',
        ).annotate(
            known_name=Lower(Coalesce('knows_as_name', 'known_character__fullname')),
            cleaned_name=Replace('known_name', Value('"'), Value('')),
            initial=Lower(Substr('cleaned_name', 1, 1))
        ).exclude(
            known_character=self
        )
        return qs

    def acquisitions_for_character_sheet(self):
        return self.acquisitions.annotate(
            type=F('skill_level__skill__types__name'),
            group=F('skill_level__skill__group__name'),
        ).prefetch_related(
            'skill_level__skill',
            'skill_level__perks__conditional_modifiers__conditions',
            'skill_level__perks__conditional_modifiers__combat_types',
            'skill_level__perks__conditional_modifiers__modifier__factor',
            'skill_level__perks__comments',
            'weapon_type__comparables',
        ).order_by(
            # order_by combined with distinct for "DISTINCT ON" query:
            # This filters out all SkillLevel-s apart from the highest one
            # https://docs.djangoproject.com/en/4.0/ref/models/querysets/#distinct
            'skill_level__skill__name',
            'weapon_type__name',
            '-skill_level__level'
        ).distinct(
            'skill_level__skill__name',
            'weapon_type__name',
        )

    def synergies_for_character_sheet(self):
        from rules.models import Synergy, SynergyLevel
        skill_levels = self.skill_levels.all()
        synergy_levels = SynergyLevel.objects.prefetch_related('skill_levels')
        synergy_levels_ids = [
            synergy_lvl.id for synergy_lvl in synergy_levels
            if all(
                [(skill_lvl in skill_levels) for skill_lvl in synergy_lvl.skill_levels.all()])
        ]
        synergy_levels = synergy_levels.filter(
            id__in=synergy_levels_ids
        ).prefetch_related(
            'synergy__skills',
            'perks__conditional_modifiers__conditions',
            'perks__conditional_modifiers__combat_types',
            'perks__conditional_modifiers__modifier__factor',
            'perks__comments',
            'skill_levels__skill',
        ).order_by(
            # order_by combined with distinct for "DISTINCT ON" query:
            # This filters out all SkillLevel-s apart from the highest one
            # https://docs.djangoproject.com/en/4.0/ref/models/querysets/#distinct
            'synergy__name',
            '-level',
        ).distinct(
            'synergy__name',
        )

        synergies = Synergy.objects.filter(
            synergy_levels__in=synergy_levels
        ).prefetch_related(
            Prefetch('synergy_levels', queryset=synergy_levels)
        ).distinct()

        return synergies

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
            'kinds',
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


class CharacterSpellAcquisitions(Character):
    """A class to enable a separate AdminModel-s."""

    class Meta:
        proxy = True
        verbose_name = '*Character (Spell Acquisitions)'
        verbose_name_plural = '*Characters (Spell Acquisitions)'


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
    knows_as_name = CharField(max_length=100, blank=True, null=True)
    knows_as_description = TextField(blank=True, null=True)
    knows_as_image = ImageField(upload_to='profile_pics', blank=True)

    class Meta:
        ordering = [OrderByPolish('known_character__fullname')]
        unique_together = ['known_character', 'knowing_character']

    def __str__(self):
        return f"{self.knowing_character} -> {self.known_character}"


class AcquaintanceshipProxyManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs


class AcquaintanceshipProxy(Acquaintanceship):
    """A proxy model to create another __str__ representation."""
    # TODO this is to ensure knows_as_name in CreateDebateForm. Any better way?

    objects = AcquaintanceshipProxyManager()

    class Meta:
        proxy = True

    def __str__(self):
        if self.knows_as_name and self.knows_as_name != "":
            return self.knows_as_name
        return self.known_character.fullname


# -----------------------------------------------------------------------------


class Acquisition(Model):
    character = FK(to=Character, related_name='acquisitions', on_delete=CASCADE)
    skill_level = FK(to=SkillLevel, related_name='acquisitions', on_delete=CASCADE)
    weapon_type = FK(to=WeaponType, on_delete=CASCADE, blank=True, null=True)

    class Meta:
        ordering = [
            OrderByPolish('character__fullname'),
            OrderByPolish('skill_level__skill__name'),
            'skill_level__level'
        ]
        # ordering = ['character__fullname', 'skill_level__skill__name', 'skill_level__level']
        unique_together = [
            ['character', 'skill_level', 'weapon_type'],
        ]

    def __str__(self):
        weapon_type = f" {self.weapon_type}" if self.weapon_type else ""
        return f"{self.character}: {self.skill_level}{weapon_type}"


# -----------------------------------------------------------------------------


class SpellAcquisition(Model):
    character = FK(Character, related_name='spellacquisitions', on_delete=CASCADE)
    spell = FK(Spell, related_name='spellacquisitions', on_delete=CASCADE)
    sphragis = FK(Domain, related_name='spellacquisitions', on_delete=PROTECT, blank=True, null=True)
    sphere = FK(Sphere, related_name='spellacquisitions', on_delete=PROTECT, blank=True, null=True)

    class Meta:
        ordering = [
            OrderByPolish('character__fullname'),
            'spell__level',
            OrderByPolish('spell__name'),
        ]
        unique_together = [
            ['character', 'spell', 'sphragis'],
        ]

    def __str__(self):
        sphragis = f" ({self.sphragis})" if self.sphragis else ""
        return f"{self.character}: {self.spell}{sphragis}"


# ---------------------------------------

# Signals


@receiver(post_save, sender=Character)
def update_acquaintanceships(sender, instance, created, **kwargs):
    """Make an Acquaintance for GMs -> new Character."""
    if created:
        for gm_character in Character.objects.filter(profile__status='gm'):
            Acquaintanceship.objects.create(
                knowing_character=gm_character,
                known_character=instance,
                is_direct=True,
                knows_if_dead=True)


@receiver(post_save, sender=Character)
@receiver(post_save, sender=Acquaintanceship)
def remove_cache(sender, instance, **kwargs):
    """
    Clear relevant Acquantainceship fragment cache on
    Character/Acquaintanceship save.
    """
    if isinstance(instance, Acquaintanceship):
        character = instance.known_character
        userids = [instance.knowing_character.profile.user.id]
    elif isinstance(instance, Character):
        character = instance
        userids = set(
            acq.knowing_character.profile.user.id
            for acq in Acquaintanceship.objects.filter(known_character=character)
        )
    else:
        raise Exception('Unimplemented Prosoponomikon signal!')

    vary_on_list = [[userid, character.id] for userid in userids]

    clear_cache(cachename='prosoponomikon-acquaintanceships', vary_on_list=vary_on_list)
    clear_cache(cachename='prosoponomikon-acquaintanceship', vary_on_list=vary_on_list)


@receiver(post_save, sender=Character.skill_levels.through)
@receiver(post_save, sender=Character.spells.through)
def remove_cache(sender, instance, **kwargs):
    """
    Clear relevant Acquantainceship fragment cache on
    Acquisition (skill_levels) change.
    """
    userids = profiles_to_userids(
        Profile.objects.filter(Q(status='gm') | Q(id=instance.character.profile.id))
    )
    vary_on_list = [[userid, instance.character.id] for userid in userids]

    clear_cache(cachename='prosoponomikon-acquaintanceship', vary_on_list=vary_on_list)


@receiver(post_save, sender='items.Item')
def remove_cache(sender, instance, **kwargs):
    """
    Clear relevant Acquantainceship fragment cache on Item save.
    """
    userids = profiles_to_userids(
        Profile.objects.filter(
            Q(status='gm') | Q(id=instance.collection.owner.profile.id))
    )
    vary_on_list = [[userid, instance.collection.owner.id] for userid in userids]

    clear_cache(cachename='prosoponomikon-acquaintanceship', vary_on_list=vary_on_list)


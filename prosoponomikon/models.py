from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    ForeignKey as FK,
    Manager,
    ManyToManyField as M2M,
    Model,
    OneToOneField as OneToOne,
    PROTECT,
    Q,
    SET_NULL,
    SmallIntegerField,
    TextField, IntegerField
)
from django.db.models.signals import post_save
from rpg_project.utils import create_sorting_name

from imaginarion.models import Picture
from knowledge.models import BiographyPacket, DialoguePacket
from knowledge.models import KnowledgePacket
from rules.models import Skill
from toponomikon.models import Location
from users.models import Profile


class NameGroup(Model):
    title = CharField(max_length=250, unique=True)
    description = TextField(blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


NAME_TYPES = (
    ('MALE', 'MALE'),
    ('FEMALE', 'FEMALE'),
)


class AffixGroupManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('name_group')
        return qs


class AffixGroup(Model):
    objects = AffixGroupManager()
    
    affix = CharField(max_length=100)
    type = CharField(max_length=20, choices=NAME_TYPES, default='male')
    name_group = FK(
        to=NameGroup, related_name='affix_groups', on_delete=PROTECT)
    
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
    
    form = CharField(max_length=250, unique=True)
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


class FamilyName(Model):
    form = CharField(max_length=250)
    locations = M2M(to=Location, related_name="family_names", blank=True)
    
    class Meta:
        ordering = ['form']
    
    def __str__(self):
        return self.form


class CharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('first_name', 'family_name')
        return qs
    
    
class Character(Model):
    objects = CharacterManager()
    
    profile = OneToOne(to=Profile, on_delete=CASCADE)
    first_name = FK(
        to=FirstName,
        related_name='characters',
        on_delete=PROTECT,
        blank=True,
        null=True)
    family_name = FK(
        to=FamilyName,
        related_name='characters',
        on_delete=PROTECT,
        blank=True,
        null=True)
    cognomen = CharField(max_length=250, blank=True, null=True)
    description = TextField(blank=True, null=True)
    frequented_locations = M2M(
        to=Location,
        related_name='frequented_by_characters',
        blank=True)
    pictures = M2M(to=Picture, related_name='characters', blank=True)
    biography_packets = M2M(
        to=BiographyPacket,
        related_name='characters',
        blank=True)
    dialogue_packets = M2M(
        to=DialoguePacket,
        related_name='characters',
        blank=True)
    known_directly = M2M(
        to=Profile,
        related_name='characters_known_directly',
        limit_choices_to=Q(status='player'),
        blank=True)
    known_indirectly = M2M(
        to=Profile,
        related_name='characters_known_indirectly',
        limit_choices_to=Q(status='player'),
        blank=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)
    
    class Meta:
        ordering = ['sorting_name']
        verbose_name = '* CHARACTER'
        verbose_name_plural = '* CHARACTERS'
    
    def __str__(self):
        name = f"{self.first_name} " if self.first_name else ""
        family_name = f"{self.family_name} " if self.family_name else ""
        cognomen = f"{self.cognomen} " if self.cognomen else ""
        return f"{name}{family_name}{cognomen}".strip()
    
    def save(self, *args, **kwargs):
        self.sorting_name = create_sorting_name(self.__str__())
        super().save(*args, **kwargs)
    
    def all_known(self):
        return self.known_directly.all() | self.known_indirectly.all()
    
    def informables(self):
        qs = Profile.active_players.all()
        qs = qs.exclude(id__in=self.all_known())
        qs = qs.exclude(character__id=self.pk)
        return qs


class PlayerCharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(profile__status='player')
        return qs


class PlayerCharacter(Character):
    objects = PlayerCharacterManager()
    
    class Meta:
        proxy = True
        verbose_name = '--- Player'
        verbose_name_plural = '--- Players'


class NPCCharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(profile__status='npc')
        return qs


class NPCCharacter(Character):
    objects = NPCCharacterManager()
    
    class Meta:
        proxy = True
        verbose_name = '--- NPC'
        verbose_name_plural = '--- NPCs'


class CharacterGroup(Model):
    """A mnodel for storing default knowledge packet sets for groups of
     characters. These should be automatically added to the knowlege packets of
     a newly created Character that belongs to a CharacterGroup (by signals).
    """
    name = CharField(max_length=250, verbose_name='Nazwa grupy')
    author = FK(
        to=Profile,
        related_name='character_groups_authored',
        on_delete=SET_NULL,
        blank=True,
        null=True,
    )
    characters = M2M(
        to=Character,
        related_name='character_groups',
        verbose_name='Zgrupowane postacie'
    )
    default_knowledge_packets = M2M(
        to=KnowledgePacket,
        related_name='character_group_defaults',
        blank=True,
        verbose_name='Domyślne pakiety wiedzy NPC w grupie',
    )
    default_skills = M2M(
        to=Skill,
        related_name='character_group_defaults',
        blank=True,
        verbose_name='Domyślne umiejętności NPC w grupie',
    )
    order_no = SmallIntegerField(default=1, verbose_name='Nr porządkowy')
    
    class Meta:
        ordering = ['order_no', 'name']
        unique_together = ('name', 'author')
        verbose_name = '* CHARACTER GROUP'
        verbose_name_plural = '* CHARACTER GROUPS'
    
    def __str__(self):
        return f"{self.name} [{self.author}]"


def copy_name_from_character_to_profile(sender, instance, **kwargs):
    profile = instance.profile
    profile.copied_character_name = str(instance)
    profile.save()


post_save.connect(copy_name_from_character_to_profile, sender=Character)
post_save.connect(copy_name_from_character_to_profile, sender=NPCCharacter)
post_save.connect(copy_name_from_character_to_profile, sender=PlayerCharacter)

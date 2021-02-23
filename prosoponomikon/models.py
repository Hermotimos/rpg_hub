from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    ForeignKey as FK,
    IntegerField,
    Manager,
    ManyToManyField as M2M,
    Model,
    OneToOneField as OneToOne,
    PROTECT,
    Q,
    SET_NULL,
    SmallIntegerField,
    TextField,
)
from django.db.models.signals import post_save
from rpg_project.utils import create_sorting_name

from imaginarion.models import Picture
from knowledge.models import BiographyPacket, DialoguePacket
from knowledge.models import KnowledgePacket
from toponomikon.models import Location
from users.models import Profile


class NameContinuum(Model):
    description = TextField(blank=True, null=True)

    def __str__(self):
        if self.name_forms.all():
            return " | ".join([str(name) for name in self.name_forms.all()])
        return "No names yet"
    
    
class NameGroup(Model):
    title = CharField(max_length=250)
    description = TextField(blank=True, null=True)

    def __str__(self):
        return self.title


NAME_TYPES = (
    ('male', 'MALE'),
    ('female', 'FEMALE'),
    ('daemon', 'DAEMON'),
)


class NameForm(Model):
    form = CharField(max_length=250)
    name_continuum = FK(
        to=NameContinuum,
        related_name="name_forms",
        on_delete=PROTECT,
        blank=True,
        null=True)
    type = CharField(max_length=20, choices=NAME_TYPES, default='male')
    is_ancient = BooleanField(default=False)
    name_groups = M2M(to=NameGroup, related_name='names', blank=True)
    locations = M2M(to=Location, related_name="names", blank=True)
    
    class Meta:
        ordering = ['form']

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
        qs = qs.select_related('name', 'family_name')
        return qs
    
    
class Character(Model):
    objects = CharacterManager()
    
    profile = OneToOne(to=Profile, on_delete=CASCADE)
    name = FK(
        to=NameForm,
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
    frequented_locations = M2M(
        to=Location,
        related_name='frequented_by_characters',
        blank=True,
    )
    pictures = M2M(to=Picture, related_name='characters', blank=True)
    description = TextField(blank=True, null=True)
    biography_packets = M2M(
        to=BiographyPacket,
        related_name='characters',
        blank=True,
    )
    dialogue_packets = M2M(
        to=DialoguePacket,
        related_name='characters',
        blank=True,
    )
    known_directly = M2M(
        to=Profile,
        related_name='characters_known_directly',
        limit_choices_to=Q(status='player'),
        blank=True,
    )
    known_indirectly = M2M(
        to=Profile,
        related_name='characters_known_indirectly',
        limit_choices_to=Q(status='player'),
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)
    
    class Meta:
        ordering = ['sorting_name']
        verbose_name = '* CHARACTER'
        verbose_name_plural = '* CHARACTERS'
    
    def __str__(self):
        name = f"{self.name} " if self.name else ""
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

from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey as FK,
    Manager,
    ManyToManyField as M2M,
    Model,
    OneToOneField,
    PROTECT,
    Q,
    SET_NULL,
    PositiveSmallIntegerField,
    TextField,
)
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from rpg_project.utils import create_sorting_name

from imaginarion.models import Picture
from knowledge.models import BiographyPacket, DialoguePacket
from knowledge.models import KnowledgePacket
from toponomikon.models import Location
from users.models import Profile


PLAYER_STATUS = [
    'active_player',
    'inactive_player',
    'dead_player',
]


class Character(Model):
    profile = OneToOneField(to=Profile, on_delete=CASCADE)
    name = CharField(max_length=100)
    descr_origin = TextField(blank=True, null=True)
    descr_occupation = TextField(blank=True, null=True)
    descr_psychophysical = TextField(blank=True, null=True)
    descr_for_gm = TextField(blank=True, null=True)
    known_directly = M2M(
        to=Profile,
        related_name='characters_known_directly',
        limit_choices_to=Q(status__in=PLAYER_STATUS),
        blank=True,
    )
    known_indirectly = M2M(
        to=Profile,
        related_name='characters_known_indirectly',
        limit_choices_to=Q(status__in=PLAYER_STATUS),
        blank=True,
    )
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
    birth_location = FK(
        to=Location,
        related_name='characters_born',
        on_delete=PROTECT,
    )
    locations = M2M(to=Location, related_name='characters', blank=True)
    pictures = M2M(to=Picture, related_name='characters', blank=True)
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
    
    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
 
    
class PlayerCharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(profile__status__in=PLAYER_STATUS))
        return qs
    
    
class PlayerCharacter(Character):
    objects = PlayerCharacterManager()
    
    class Meta:
        proxy = True


class NonPlayerCharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(Q(profile__status__in=PLAYER_STATUS))
        return qs


class NonPlayerCharacter(Character):
    objects = NonPlayerCharacterManager()
    
    class Meta:
        proxy = True


class CharacterGroup(Model):
    """A mnodel for storing default knowledge packet sets for groups of
     characters. These should be automatically added to the knowlege packets of
     a newly created character that belongs to a CharacterGroup (by signals).
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
        verbose_name='Domyślne umiejętności zgrupowanych postaci',
    )
    order_no = PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Numer porządkowy grupy [opcjonalnie]:',
    )
    
    class Meta:
        ordering = ['order_no', 'name']
    
    def __str__(self):
        return f"{self.name} [{self.author}]"
    
    # TODO: grous: 'Gracze', 'Tirsenowie', 'Skadyjczycy'
    
    # TODO no signal necessary to include knowledge packets on per group basis
    # TODO -> show them by character.character_groups.knowledge_packets ...


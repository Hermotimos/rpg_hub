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
    TextField,
)
# from django.db.models.signals import post_save
# from django.dispatch import receiver

from imaginarion.models import Picture
from knowledge.models import BiographyPacket, DialoguePacket
from knowledge.models import KnowledgePacket
from toponomikon.models import Location
from users.models import Profile

PLAYERS = Q(status__in=[
    'active_player',
    'inactive_player',
    'dead_player',
])


class CharacterGroup(Model):
    """A mnodel for storing default knowledge packet sets for groups of
     characters. These should be automatically added to the knowlege packets of
     a newly created character that belongs to a CharacterGroup (by signals).
    """
    name = CharField(max_length=250)
    knowledge_packets = M2M(
        to=KnowledgePacket,
        related_name='character_groups',
        blank=True,
    )
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    # TODO no signal necessary to include knowledge packets on per group basis
    # TODO -> show them by character.character_groups.knowledge_packets ...


class Character(Model):
    profile = OneToOneField(to=Profile, on_delete=CASCADE)

    def get_character_name(self):
        return self.profile.character_name
    character_name2 = CharField(max_length=100, default=get_character_name)
    
    description_short = CharField(max_length=250, blank=True, null=True)
    description_long = TextField(blank=True, null=True)
    character_groups = M2M(
        to=CharacterGroup,
        related_name='characters',
        blank=True,
    )
    known_directly = M2M(
        to='self',
        related_name='characters_known_directly',
        limit_choices_to=PLAYERS,
        blank=True,
    )
    known_indirectly = M2M(
        to='self',
        related_name='characters_known_indirectly',
        limit_choices_to=PLAYERS,
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
    
    class Meta:
        ordering = ['character_name2']
    
    def __str__(self):
        return self.character_name2




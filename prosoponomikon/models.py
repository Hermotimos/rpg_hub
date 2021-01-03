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


class Persona(Model):
    profile = FK(to=Profile, related_name='personas', on_delete=CASCADE)
    name = CharField(max_length=100)
    birth_location = FK(
        to=Location,
        related_name='personas_born',
        on_delete=PROTECT,
    )
    visited_locations = M2M(to=Location, related_name='visiting_personas', blank=True)
    picture_main = OneToOneField(
        to=Picture,
        on_delete=SET_NULL,
        blank=True,
        null=True,
    )
    pictures = M2M(to=Picture, related_name='personas', blank=True)
    description_main = TextField(blank=True, null=True)
    biography_packets = M2M(
        to=BiographyPacket,
        related_name='personas',
        blank=True,
    )
    dialogue_packets = M2M(
        to=DialoguePacket,
        related_name='personas',
        blank=True,
    )
    known_directly = M2M(
        to=Profile,
        related_name='personas_known_directly',
        limit_choices_to=Q(status__in=PLAYER_STATUS),
        blank=True,
    )
    known_indirectly = M2M(
        to=Profile,
        related_name='personas_known_indirectly',
        limit_choices_to=Q(status__in=PLAYER_STATUS),
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
    
    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
 
    
class PlayerPersonaManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(Q(profile__status__in=PLAYER_STATUS))
        return qs
    
    
class PlayerPersona(Persona):
    objects = PlayerPersonaManager()
    
    class Meta:
        proxy = True


class NonPlayerPersonaManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(Q(profile__status__in=PLAYER_STATUS))
        return qs


class NonPlayerPersona(Persona):
    objects = NonPlayerPersonaManager()
    
    class Meta:
        proxy = True


class PersonaGroup(Model):
    """A mnodel for storing default knowledge packet sets for groups of
     personas. These should be automatically added to the knowlege packets of
     a newly created Persona that belongs to a PersonaGroup (by signals).
    """
    name = CharField(max_length=250, verbose_name='Nazwa grupy')
    author = FK(
        to=Profile,
        related_name='persona_groups_authored',
        on_delete=SET_NULL,
        blank=True,
        null=True,
    )
    personas = M2M(
        to=Persona,
        related_name='persona_groups',
        verbose_name='Zgrupowane postacie'
    )
    default_knowledge_packets = M2M(
        to=KnowledgePacket,
        related_name='persona_group_defaults',
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


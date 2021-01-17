from django.db.models import (
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
    PositiveSmallIntegerField,
    TextField,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from rpg_project.utils import create_sorting_name

from imaginarion.models import Picture
from knowledge.models import BiographyPacket, DialoguePacket
from knowledge.models import KnowledgePacket
from toponomikon.models import Location
from users.models import Profile


class Persona(Model):
    profile = OneToOne(to=Profile, on_delete=CASCADE)
    name = CharField(max_length=100)
    birth_location = FK(
        to=Location,
        related_name='personas_born',
        on_delete=PROTECT,
    )
    frequented_locations = M2M(
        to=Location,
        related_name='frequented_by_personas',
        blank=True,
    )
    pictures = M2M(to=Picture, related_name='personas', blank=True)
    description = TextField(blank=True, null=True)
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
        limit_choices_to=Q(status='player'),
        blank=True,
    )
    known_indirectly = M2M(
        to=Profile,
        related_name='personas_known_indirectly',
        limit_choices_to=Q(status='player'),
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        verbose_name = '* PERSONAS'
        verbose_name_plural = '* PERSONAS'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)
        
    def all_known(self):
        return self.known_directly.all() | self.known_indirectly.all()

    def informables(self):
        qs = Profile.active_players.all()
        qs = qs.exclude(id__in=self.all_known())
        return qs
    
    
class PlayerPersonaManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(profile__status='player')
        return qs
    
    
class PlayerPersona(Persona):
    objects = PlayerPersonaManager()
    
    class Meta:
        proxy = True
        verbose_name = '--- Player'
        verbose_name_plural = '--- Players'


class NPCPersonaManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(profile__status='npc')
        return qs


class NPCPersona(Persona):
    objects = NPCPersonaManager()
    
    class Meta:
        proxy = True
        verbose_name = '--- NPC'
        verbose_name_plural = '--- NPCs'


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
        verbose_name='Domyślne umiejętności NPC w grupie',
    )
    order_no = PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Numer porządkowy grupy [opcjonalnie]',
    )
    
    class Meta:
        ordering = ['order_no', 'name']
        verbose_name = '* PERSONA GROUP'
        verbose_name_plural = '* PERSONA GROUPS'
    
    def __str__(self):
        return f"{self.name} [{self.author}]"
    

@receiver(post_save, sender=Persona)
def create_profile(sender, instance, created, **kwargs):
    profile = instance.profile
    profile.copied_character_name = instance.name
    profile.save()
    if created:
        profile = instance.profile
        profile.copied_character_name = instance.name
        profile.save()

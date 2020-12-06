from django.db.models import (
    CharField,
    ForeignKey as FK,
    Manager,
    ManyToManyField as M2MField,
    Model,
    PositiveSmallIntegerField,
    PROTECT,
    Q,
    SET_NULL,
    TextField,
)
from django.db.models.signals import post_save, m2m_changed

from imaginarion.models import AudioSet, Picture
from knowledge.models import KnowledgePacket, MapPacket
from rpg_project.utils import create_sorting_name
from users.models import Profile

PLAYERS = Q(status__in=[
    'active_player',
    'inactive_player',
    'dead_player',
])


class LocationType(Model):
    name = CharField(max_length=100)
    name_plural = CharField(max_length=100, blank=True, null=True)
    default_img = FK(
        to=Picture,
        related_name='location_types',
        on_delete=SET_NULL,
        null=True,
    )
    order_no = PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['order_no']

    def __str__(self):
        return self.name


class Location(Model):
    name = CharField(unique=True, max_length=100)
    description = TextField(blank=True, null=True)
    main_image = FK(
        to=Picture,
        related_name='locations_main_pics',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    pictures = M2MField(to=Picture, related_name='locations_pics', blank=True)
    audio_set = FK(
        to=AudioSet,
        related_name='locations',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    knowledge_packets = M2MField(
        to=KnowledgePacket,
        related_name='locations',
        blank=True,
    )
    map_packets = M2MField(to=MapPacket, related_name='locations', blank=True)
    location_type = FK(
        to=LocationType,
        related_name='locations',
        on_delete=PROTECT,
        null=True,
    )
    in_location = FK(
        to='self',
        related_name='locations',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    known_directly = M2MField(
        to=Profile,
        related_name='locs_known_directly',
        limit_choices_to=PLAYERS,
        blank=True,
    )
    known_indirectly = M2MField(
        to=Profile,
        related_name='locs_known_indirectly',
        limit_choices_to=PLAYERS,
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

    def informables(self):
        qs = Profile.objects.filter(status__in=[
            'active_player',
        ])
        qs = qs.exclude(
            id__in=(self.known_directly.all() | self.known_indirectly.all())
        )
        return qs


class PrimaryLocationManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(in_location=None)
        return qs


class PrimaryLocation(Location):
    objects = PrimaryLocationManager()
    
    class Meta:
        proxy = True
        
        
class SecondaryLocationManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(~Q(in_location=None))
        # In case of TertiaryLocation:
        # qs = qs.filter(in_location__in_location=None)
        return qs


class SecondaryLocation(Location):
    objects = SecondaryLocationManager()
    
    class Meta:
        proxy = True
        

def update_known_gen_locations(sender, instance, **kwargs):
    """Whenever a location becomes 'known_directly' or 'known_indirectly' to
    a profile, add this location's 'in_location' (i.e. more general location)
    to profile's 'known_directly' or 'known_indirectly', respectively.
    """
    known_directly = instance.known_directly.all()
    known_indirectly = instance.known_indirectly.all()
    in_location = instance.in_location
    if in_location:
        in_location.known_directly.add(*known_directly)
        in_location.known_indirectly.add(*known_indirectly)


post_save.connect(update_known_gen_locations, sender=Location)
m2m_changed.connect(update_known_gen_locations,
                    sender=Location.known_directly.through)
m2m_changed.connect(update_known_gen_locations,
                    sender=Location.known_indirectly.through)

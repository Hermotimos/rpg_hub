from django.db.models import (
    CharField,
    ForeignKey as FK,
    Manager,
    ManyToManyField as M2M,
    Model,
    PositiveSmallIntegerField,
    PROTECT,
    Q,
    SET_NULL,
    TextField,
)
from django.db.models.signals import post_save, m2m_changed

from imaginarion.models import AudioSet, Picture, PictureSet
from knowledge.models import KnowledgePacket, MapPacket
from rpg_project.utils import create_sorting_name
from users.models import Profile


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
        verbose_name = '* LOCATION TYPE'
        verbose_name_plural = '* LOCATION TYPES'

    def __str__(self):
        return self.name


class LocationManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        # No select_related, as it greatly increases queries in LocationAdmin
        return qs


class Location(Model):
    objects = LocationManager()
    
    name = CharField(unique=True, max_length=100)
    description = TextField(blank=True, null=True)
    main_image = FK(
        to=Picture,
        related_name='locations_main_pics',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    picture_sets = M2M(to=PictureSet, related_name='locations', blank=True)
    audio_set = FK(
        to=AudioSet,
        related_name='locations',
        on_delete=PROTECT,
        blank=True,
        null=True,
    )
    knowledge_packets = M2M(to=KnowledgePacket, related_name='locations', blank=True)
    map_packets = M2M(to=MapPacket, related_name='locations', blank=True)
    
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
    participants = M2M(
        to=Profile,
        related_name='locations_participated',
        limit_choices_to=Q(status='player'),
        blank=True,
    )
    known_indirectly = M2M(
        to=Profile,
        related_name='locs_known_indirectly',
        limit_choices_to=Q(status='player'),
        blank=True,
    )
    sorting_name = CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ['sorting_name']
        verbose_name = '* LOCATION'
        verbose_name_plural = '* LOCATIONS'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super().save(*args, **kwargs)

    def informables(self):
        qs = Profile.active_players.all()
        qs = qs.exclude(
            id__in=(self.participants.all() | self.known_indirectly.all())
        )
        return qs
    
    def with_sublocations(self):
        with_sublocs = Location.objects.raw(f"""
            WITH RECURSIVE sublocations AS (
                SELECT * FROM toponomikon_location WHERE id = {self.pk}
                UNION ALL
                SELECT loc.*
                FROM toponomikon_location AS loc JOIN sublocations AS subloc
                    ON loc.in_location_id = subloc.id
            )
            SELECT * FROM sublocations;
        """)
        return with_sublocs


class PrimaryLocationManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(in_location=None)
        return qs


class PrimaryLocation(Location):
    objects = PrimaryLocationManager()
    
    class Meta:
        proxy = True
        verbose_name = '--- Primary Location'
        verbose_name_plural = '--- Primary Locations'

        
class SecondaryLocationManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(~Q(in_location=None))
        return qs


class SecondaryLocation(Location):
    objects = SecondaryLocationManager()
    
    class Meta:
        proxy = True
        verbose_name = '--- Secondary Location'
        verbose_name_plural = '--- Secondary Locations'


def update_known_locations(sender, instance, **kwargs):
    """Whenever a location becomes 'participants' or 'known_indirectly' to
    a profile, add this location's 'in_location' (i.e. more general location)
    to profile's 'participants' or 'known_indirectly', respectively.
    """
    participants = instance.participants.all()
    known_indirectly = instance.known_indirectly.all()
    in_location = instance.in_location
    if in_location:
        in_location.participants.add(*participants)
        in_location.known_indirectly.add(*known_indirectly)


post_save.connect(update_known_locations, sender=Location)
m2m_changed.connect(update_known_locations,
                    sender=Location.participants.through)
m2m_changed.connect(update_known_locations,
                    sender=Location.known_indirectly.through)

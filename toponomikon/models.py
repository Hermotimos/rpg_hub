from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed

from imaginarion.models import Audio, Picture
from knowledge.models import KnowledgePacket
from rpg_project.utils import create_sorting_name
from users.models import Profile


class LocationType(models.Model):
    name = models.CharField(max_length=100)
    name_plural = models.CharField(max_length=100, blank=True, null=True)
    default_img = models.ForeignKey(
        to=Picture,
        related_name='location_types',
        on_delete=models.SET_NULL,
        null=True,
    )
    order_no = models.PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['order_no']

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    main_image = models.ForeignKey(
        to=Picture,
        blank=True,
        null=True,
        related_name='locations_main_pics',
        on_delete=models.PROTECT,
    )
    # audio_path = models.TextField(blank=True, null=True)
    audio = models.ForeignKey(
        to=Audio,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    pictures = models.ManyToManyField(
        to=Picture,
        blank=True,
        related_name='locations_pics'
    )
    knowledge_packets = models.ManyToManyField(
        to=KnowledgePacket,
        blank=True,
        related_name='locations'
    )
    location_type = models.ForeignKey(
        to=LocationType,
        null=True,
        related_name='locations',
        on_delete=models.PROTECT,
    )
    in_location = models.ForeignKey(
        to='self',
        blank=True,
        null=True,
        related_name='locations',
        on_delete=models.PROTECT,
    )
    known_directly = models.ManyToManyField(
        to=Profile,
        blank=True,
        related_name='locs_known_directly',
        limit_choices_to=Q(
            status__in=['active_player', 'inactive_player', 'dead_player']
        ),
    )
    known_indirectly = models.ManyToManyField(
        to=Profile,
        blank=True,
        related_name='locs_known_indirectly',
        limit_choices_to=Q(
            status__in=['active_player', 'inactive_player', 'dead_player']
        ),
    )
    sorting_name = models.CharField(max_length=250, blank=True, null=True)

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


class PrimaryLocationManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(in_location=None)
        return qs


class PrimaryLocation(Location):
    objects = PrimaryLocationManager()
    
    class Meta:
        proxy = True
        
        
class SecondaryLocationManager(models.Manager):
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
        

# class TertiaryLocationManager(models.Manager):
#     def get_queryset(self):
#         qs = super().get_queryset()
#         qs = qs.filter(~Q(in_location__in_location=None))
#         return qs
#
#
# class TertiaryLocation(Location):
#     objects = TertiaryLocationManager()
#
#     class Meta:
#         proxy = True
#

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

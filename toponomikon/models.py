from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed

from imaginarion.models import Picture
from knowledge.models import KnowledgePacket
from rpg_project.utils import create_sorting_name
from users.models import Profile


class LocationType(models.Model):
    name = models.CharField(max_length=100)
    name_plural = models.CharField(max_length=100, blank=True, null=True)
    default_img = models.ForeignKey(to=Picture, related_name='location_types',
                                    on_delete=models.SET_NULL, null=True)
    order_no = models.SmallIntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    
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
        on_delete=models.SET_NULL,
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
            status__in=[
                'active_player',
                'inactive_player',
                'dead_player'
            ]
        ),
    )
    known_indirectly = models.ManyToManyField(
        to=Profile,
        blank=True,
        related_name='locs_known_indirectly',
        limit_choices_to=Q(
            status__in=[
                'active_player',
                'inactive_player',
                'dead_player'
            ]
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

    def informable(self):
        known_directly = self.known_directly.all()
        known_indirectly = self.known_indirectly.all()
        excluded = (known_directly | known_indirectly).distinct()
        informable = Profile.objects.filter(
            status='active_player'
        ).exclude(id__in=excluded)
        return informable


class MainLocationManager(models.Manager):
    
    def get_queryset(self):
        qs = super(MainLocationManager, self).get_queryset()
        return qs.filter(in_location=None)


class MainLocation(Location):
    objects = MainLocationManager()
    
    class Meta:
        proxy = True
        

def update_known_gen_locations(sender, instance, **kwargs):
    """Whenever a location becomes 'known_directly' or 'known_indirectly' to
    a profile, add this location's 'in_location' (i.e. more general location)
    to profile's 'known_directly' or 'known_indirectly', respectively.
    """
    known_directly = instance.known_directly.all()
    known_indirectly = instance.known_indirectly.all()
    gen_location = instance.in_location
    if gen_location:
        gen_location.known_directly.add(*known_directly)
        gen_location.known_indirectly.add(*known_indirectly)


post_save.connect(update_known_gen_locations, sender=Location)
m2m_changed.connect(update_known_gen_locations,
                    sender=Location.known_directly.through)
m2m_changed.connect(update_known_gen_locations,
                    sender=Location.known_indirectly.through)

from django.conf import settings
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
from django.dispatch import receiver
from django.urls import reverse

from imaginarion.models import AudioSet, Picture, PictureSet
from knowledge.models import KnowledgePacket, MapPacket
from rpg_project.utils import OrderByPolish, clear_cache, profiles_to_userids

from users.models import Profile


class LocationType(Model):
    name = CharField(unique=True, max_length=100)
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


class Location(Model):
    name = CharField(max_length=100)
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
    informees = M2M(
        to=Profile,
        related_name='locations_informed',
        limit_choices_to=Q(status='player'),
        blank=True,
    )

    class Meta:
        ordering = [OrderByPolish('name')]
        unique_together = ['name', 'location_type']
        verbose_name = 'Location'
        verbose_name_plural = '--- LOCATIONS'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        print(settings.BASE_URL + reverse('toponomikon:location', kwargs={'location_id' : self.id}))
        return settings.BASE_URL + reverse('toponomikon:location', kwargs={'location_id' : self.id})

    def informables(self, current_profile):
        qs = current_profile.character.acquaintanceships()
        qs = qs.exclude(
            known_character__profile__in=(self.participants.all() | self.informees.all())
        ).filter(
            known_character__profile__in=Profile.active_players.all())

        # TODO temp 'Ilen z Astinary, Alora z Astinary'
        # hide Davos from Ilen and Alora
        if current_profile.id in [5, 6]:
            qs = qs.exclude(known_character__profile__id=3)
        # vice versa
        if current_profile.id == 3:
            qs = qs.exclude(known_character__profile__id__in=[5, 6])
        # TODO end temp

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
        qs = qs.exclude(in_location=None)
        return qs


class SecondaryLocation(Location):
    objects = SecondaryLocationManager()

    class Meta:
        proxy = True
        verbose_name = '--- Secondary Location'
        verbose_name_plural = '--- Secondary Locations'


# ---------------------------------------

# Signals


@receiver(post_save, sender=Location)
@receiver(m2m_changed, sender=Location.participants.through)
@receiver(m2m_changed, sender=Location.informees.through)
def update_known_locations(sender, instance, **kwargs):
    """
    Whenever a Location gets new 'participants'/'informees' propagate to parent
    Location's (instance.in_location) 'participants'/'informees', respectively.
    """
    participants = instance.participants.all()
    informees = instance.informees.all()
    if in_location := instance.in_location:
        in_location.participants.add(*participants)
        in_location.informees.add(*informees)


@receiver(post_save, sender=Location)
@receiver(post_save, sender=PrimaryLocation)
@receiver(post_save, sender=SecondaryLocation)
def remove_cache(sender, instance, **kwargs):
    """
    Clear relevant toponomikon cache on Location save.
    """
    userids = profiles_to_userids(
        Profile.objects.filter(status='gm')
        | instance.participants.all()
        | instance.informees.all()
    )

    if instance.in_location is None:
        cachename = 'toponomikon-primary'
        vary_on_list = [[userid] for userid in userids]
    else:
        cachename = 'toponomikon-secondary'
        vary_on_list = [[userid, instance.id] for userid in userids]

    clear_cache(cachename=cachename, vary_on_list=vary_on_list)

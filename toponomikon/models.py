from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed

from imaginarion.models import Picture
from knowledge.models import KnowledgePacket
from rpg_project.utils import create_sorting_name
from users.models import Profile


class LocationType(models.Model):
    name = models.CharField(max_length=100)
    default_img = models.ForeignKey(to=Picture, related_name='location_types',
                                    on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GeneralLocation(models.Model):
    name = models.CharField(max_length=100)
    location_type = models.ForeignKey(to=LocationType, null=True,
                                      related_name='general_locations',
                                      on_delete=models.SET_NULL)
    description = models.TextField(max_length=4000, blank=True, null=True)
    known_directly = models.ManyToManyField(
        to=Profile,
        blank=True,
        related_name='gen_locs_known_directly',
        limit_choices_to=Q(status='active_player')
                         | Q(status='inactive_player')
                         | Q(status='dead_player')
    )
    known_indirectly = models.ManyToManyField(
        to=Profile,
        blank=True,
        related_name='gen_locs_known_indirectly',
        limit_choices_to=Q(status='active_player')
                         | Q(status='inactive_player')
                         | Q(status='dead_player')
    )
    main_image = models.ForeignKey(to=Picture,  blank=True, null=True,
                                   related_name='gen_loc_main_pics',
                                   on_delete=models.PROTECT)
    knowledge_packets = models.ManyToManyField(
        to=KnowledgePacket,
        related_name='general_locations',
        blank=True
    )
    pictures = models.ManyToManyField(to=Picture, related_name='gen_loc_pics',
                                      blank=True)
    sorting_name = models.CharField(unique=True, max_length=250,
                                    blank=True, null=True)

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


class SpecificLocation(models.Model):
    name = models.CharField(max_length=100)
    location_type = models.ForeignKey(to=LocationType, null=True,
                                      related_name='specific_locations',
                                      on_delete=models.SET_NULL)
    general_location = models.ForeignKey(to=GeneralLocation,
                                         related_name='specific_locations',
                                         on_delete=models.PROTECT)
    description = models.TextField(max_length=4000, blank=True, null=True)
    known_directly = models.ManyToManyField(
        to=Profile,
        blank=True,
        related_name='spec_locs_known_directly',
        limit_choices_to=Q(status='active_player')
                         | Q(status='inactive_player')
                         | Q(status='dead_player')
    )
    known_indirectly = models.ManyToManyField(
        to=Profile,
        blank=True,
        related_name='spec_locs_known_indirectly',
        limit_choices_to=Q(status='active_player')
                         | Q(status='inactive_player')
                         | Q(status='dead_player')
    )
    main_image = models.ForeignKey(to=Picture, blank=True, null=True,
                                   related_name='spec_loc_main_pics',
                                   on_delete=models.PROTECT)
    knowledge_packets = models.ManyToManyField(
        to=KnowledgePacket,
        related_name='specific_locations',
        blank=True
    )
    pictures = models.ManyToManyField(to=Picture, related_name='spec_loc_pics',
                                      blank=True)
    sorting_name = models.CharField(unique=True, max_length=250,
                                    blank=True, null=True)

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


class Location(models.Model):
    name = models.CharField(
        unique=True,
        max_length=100)
    description = models.TextField(blank=True, null=True)
    main_image = models.ForeignKey(
        to=Picture,
        blank=True,
        null=True,
        related_name='locations_main_pics',
        # on_delete=models.CASCADE,
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
        null=True,
        related_name='locations',
        # on_delete=models.CASCADE,
        on_delete=models.PROTECT,
    )
    known_directly = models.ManyToManyField(
        to=Profile,
        blank=True,
        related_name='locations_known_directly',
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
        related_name='locations_known_indirectly',
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


def update_known_general_locations(sender, instance, **kwargs):
    known_directly = instance.known_directly.all()
    known_indirectly = instance.known_indirectly.all()
    gen_loc = instance.general_location

    gen_loc.known_directly.add(*known_directly)
    gen_loc.known_indirectly.add(*known_indirectly)


post_save.connect(update_known_general_locations,
                  sender=SpecificLocation)
m2m_changed.connect(update_known_general_locations,
                    sender=SpecificLocation.known_directly.through)
m2m_changed.connect(update_known_general_locations,
                    sender=SpecificLocation.known_indirectly.through)

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed

from imaginarion.models import Picture
from knowledge.models import KnowledgePacket
from rpg_project.utils import create_sorting_name, query_debugger
from users.models import Profile


class LocationType(models.Model):
    name = models.CharField(max_length=100)
    default_img = models.ForeignKey(Picture, related_name='location_types', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class GeneralLocation(models.Model):
    name = models.CharField(max_length=100)
    location_type = models.ForeignKey(LocationType, related_name='general_locations', on_delete=models.SET_NULL,
                                      null=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    known_directly = models.ManyToManyField(Profile,  blank=True, related_name='gen_locs_known_directly',
                                            limit_choices_to=
                                            Q(status='active_player') |
                                            Q(status='inactive_player') |
                                            Q(status='dead_player'))
    known_indirectly = models.ManyToManyField(Profile, blank=True, related_name='gen_locs_known_indirectly',
                                              limit_choices_to=
                                              Q(status='active_player') |
                                              Q(status='inactive_player') |
                                              Q(status='dead_player'))
    main_image = models.ForeignKey(Picture, related_name='gen_loc_main_pics', on_delete=models.PROTECT, blank=True,
                                   null=True)
    knowledge_packets = models.ManyToManyField(KnowledgePacket, related_name='general_locations', blank=True)
    pictures = models.ManyToManyField(Picture, related_name='gen_loc_pics', blank=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True, unique=True)

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
    location_type = models.ForeignKey(LocationType, related_name='specific_locations', on_delete=models.SET_NULL,
                                      null=True)
    general_location = models.ForeignKey(GeneralLocation, related_name='specific_locations', on_delete=models.PROTECT)
    description = models.TextField(max_length=4000, blank=True, null=True)
    known_directly = models.ManyToManyField(Profile,  blank=True,  related_name='spec_locs_known_directly',
                                            limit_choices_to=
                                            Q(status='active_player') |
                                            Q(status='inactive_player') |
                                            Q(status='dead_player'))
    known_indirectly = models.ManyToManyField(Profile,  blank=True,  related_name='spec_locs_known_indirectly',
                                              limit_choices_to=
                                              Q(status='active_player') |
                                              Q(status='inactive_player') |
                                              Q(status='dead_player'))
    main_image = models.ForeignKey(Picture, related_name='spec_loc_main_pics', on_delete=models.PROTECT, blank=True,
                                   null=True)
    knowledge_packets = models.ManyToManyField(KnowledgePacket, related_name='specific_locations', blank=True)
    pictures = models.ManyToManyField(Picture, related_name='spec_loc_pics', blank=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True, unique=True)

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


@query_debugger
def update_known_general_locations(sender, instance, **kwargs):
    known_directly = instance.known_directly.all()
    known_indirectly = instance.known_indirectly.all()
    gen_loc = instance.general_location

    gen_loc.known_directly.add(*known_directly)
    gen_loc.known_indirectly.add(*known_indirectly)


post_save.connect(update_known_general_locations, sender=SpecificLocation)
m2m_changed.connect(update_known_general_locations, sender=SpecificLocation.known_directly.through)
m2m_changed.connect(update_known_general_locations, sender=SpecificLocation.known_indirectly.through)

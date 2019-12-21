from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed

from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name, query_debugger
from users.models import Profile


class GeneralLocation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=4000, blank=True, null=True)
    known_directly = models.ManyToManyField(Profile,
                                            blank=True,
                                            limit_choices_to=
                                            Q(character_status='active_player') |
                                            Q(character_status='inactive_player') |
                                            Q(character_status='dead_player'),
                                            related_name='gen_locs_known_directly')
    known_indirectly = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='gen_locs_known_indirectly')
    main_image = models.ForeignKey(Picture,
                                   default='post_pics/topoi_gen_loc_default_MAIN.jpg',
                                   blank=True,
                                   null=True,
                                   related_name='gen_loc_main_pics',
                                   on_delete=models.PROTECT)
    pictures = models.ManyToManyField(Picture, related_name='gen_loc_pics', blank=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(GeneralLocation, self).save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']


class SpecificLocation(models.Model):
    name = models.CharField(max_length=100)
    general_location = models.ForeignKey(GeneralLocation, related_name='specific_locations', on_delete=models.PROTECT)
    description = models.TextField(max_length=4000, blank=True, null=True)
    known_directly = models.ManyToManyField(Profile,
                                            blank=True,
                                            limit_choices_to=
                                            Q(character_status='active_player') |
                                            Q(character_status='inactive_player') |
                                            Q(character_status='dead_player'),
                                            related_name='spec_locs_known_directly')
    known_indirectly = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='spec_locs_known_indirectly')
    main_image = models.ForeignKey(Picture,
                                   default='post_pics/topoi_spec_loc_default_MAIN.jpg',
                                   blank=True,
                                   null=True,
                                   related_name='spec_loc_main_pics',
                                   on_delete=models.PROTECT)
    pictures = models.ManyToManyField(Picture, related_name='spec_loc_pics', blank=True)
    sorting_name = models.CharField(max_length=250, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(SpecificLocation, self).save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']


def update_known_general_locations(sender, instance, **kwargs):
    known_directly = instance.known_directly.all()
    known_indirectly = instance.known_indirectly.all()
    gen_loc = instance.general_location

    gen_loc.known_directly.add(*known_directly)
    gen_loc.known_indirectly.add(*known_indirectly)


post_save.connect(update_known_general_locations, sender=SpecificLocation)
m2m_changed.connect(update_known_general_locations, sender=SpecificLocation.known_directly.through)
m2m_changed.connect(update_known_general_locations, sender=SpecificLocation.known_indirectly.through)

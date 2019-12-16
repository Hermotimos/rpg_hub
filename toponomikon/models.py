from django.db import models
from django.db.models import Q

from imaginarion.models import Picture
from rpg_project.utils import create_sorting_name
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
    image = models.ForeignKey(Picture, blank=True, null=True, related_name='gen_loc_pics', on_delete=models.CASCADE)
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
    image = models.ForeignKey(Picture, blank=True, null=True, related_name='spec_loc_pics', on_delete=models.CASCADE)
    sorting_name = models.CharField(max_length=250, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(SpecificLocation, self).save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']

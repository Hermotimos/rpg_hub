from PIL import Image

from django.db import models
from rpg_project.utils import create_sorting_name


class GeneralLocation(models.Model):
    name = models.CharField(max_length=100)
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
    sorting_name = models.CharField(max_length=250, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name:
            self.sorting_name = create_sorting_name(self.name)
        super(SpecificLocation, self).save(*args, **kwargs)

    class Meta:
        ordering = ['sorting_name']

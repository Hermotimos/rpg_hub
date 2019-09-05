from django.db import models
from users.models import Profile


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nazwa umiejętności')
    description = models.CharField(max_length=100, verbose_name='Opis umiejętności', blank=True, null=True)
    tested_trait = models.CharField(max_length=50, verbose_name='Cecha testowana')
    lvl0_desc = models.TextField(max_length=4000, blank=True, null=True)
    lvl1_desc = models.TextField(max_length=4000, blank=True, null=True)
    lvl2_desc = models.TextField(max_length=4000, blank=True, null=True)
    lvl3_desc = models.TextField(max_length=4000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='site_features_pics')
    allowed_profiles = models.ManyToManyField(to=Profile, related_name='allowed_skills')

    def __str__(self):
        return self.name


class Synergy(models.Model):
    skills = models.ManyToManyField(Skill, related_name='skills')
    description = models.CharField(max_length=100, verbose_name='Opis umiejętności', blank=True, null=True)
    lvl1_desc = models.TextField(max_length=4000, blank=True, null=True)
    lvl2_desc = models.TextField(max_length=4000, blank=True, null=True)
    lvl3_desc = models.TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = models.ManyToManyField(to=Profile, related_name='allowed_synergies')

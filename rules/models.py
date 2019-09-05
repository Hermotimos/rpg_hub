from django.db import models
from users.models import Profile


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Umiejętność')
    tested_trait = models.CharField(max_length=50, verbose_name='Cecha/Cechy')
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name='Opis umiejętności')
    lvl0_desc = models.TextField(max_length=4000, blank=True, null=True, verbose_name='0')
    lvl1_desc = models.TextField(max_length=4000, blank=True, null=True, verbose_name='1')
    lvl2_desc = models.TextField(max_length=4000, blank=True, null=True, verbose_name='2')
    lvl3_desc = models.TextField(max_length=4000, blank=True, null=True, verbose_name='3')
    image = models.ImageField(blank=True, null=True, upload_to='site_features_pics')
    allowed_profiles = models.ManyToManyField(to=Profile, related_name='allowed_skills', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Synergy(models.Model):
    skills = models.ManyToManyField(Skill, related_name='skills')
    description = description = models.TextField(max_length=1000, blank=True, null=True, verbose_name='Opis synergii')
    lvl1_desc = models.TextField(max_length=4000, blank=True, null=True, verbose_name='1')
    lvl2_desc = models.TextField(max_length=4000, blank=True, null=True, verbose_name='2')
    lvl3_desc = models.TextField(max_length=4000, blank=True, null=True, verbose_name='3')
    image = models.ImageField(blank=True, null=True, upload_to='site_features_pics')
    allowed_profiles = models.ManyToManyField(to=Profile, related_name='allowed_synergies', blank=True)

    def __str_(self):
        return ' + '.join(s.name for s in self.skills.all())

    def name(self):
        return self.__str_()

    class Meta:
        verbose_name = 'Synergy'
        verbose_name_plural = 'Synergies'

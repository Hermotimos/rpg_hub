from django.db import models
from django.db.models import Q
from users.models import Profile


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Umiejętność')
    tested_trait = models.CharField(max_length=50, verbose_name='Cecha/Cechy')
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name='Opis')
    lvl_0 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_1 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_2 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_3 = models.TextField(max_length=4000, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='site_features_pics')
    allowed_profiles = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='allowed_skills')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def short_name(self):
        return ''.join(word[:3] for word in str(self.name).split(' '))


class Synergy(models.Model):
    skills = models.ManyToManyField(Skill, related_name='skills')
    lvl_1 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_2 = models.TextField(max_length=4000, blank=True, null=True)
    lvl_3 = models.TextField(max_length=4000, blank=True, null=True)
    allowed_profiles = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='allowed_synergies',)

    def __str_(self):
        return ' + '.join(s.name for s in self.skills.all())

    def name(self):
        return self.__str_()

    def short_name(self):
        return ''.join(s.name[:3] for s in self.skills.all())

    class Meta:
        verbose_name = 'Synergy'
        verbose_name_plural = 'Synergies'


class CharacterClass(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=4000, blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Character class'
        verbose_name_plural = 'Character classes'

    def __str__(self):
        return self.name

    def allowed_list(self):
        allowed_profiles = []
        for profession in self.professions.all():
            for profile in profession.allowed_profiles.all():
                allowed_profiles.append(profile)
        return allowed_profiles

    def short_name(self):
        return ''.join(word[:4] for word in str(self.name).split(' '))


class CharacterProfession(models.Model):
    name = models.CharField(max_length=100, unique=True)
    character_class = models.ForeignKey(CharacterClass, related_name='professions', on_delete=models.PROTECT)
    description = models.TextField(max_length=4000, blank=True, null=True)
    start_perks = models.TextField(max_length=4000, blank=True, null=True)
    lvl_1 = models.CharField(max_length=500, blank=True, null=True)
    lvl_2 = models.CharField(max_length=500, blank=True, null=True)
    lvl_3 = models.CharField(max_length=500, blank=True, null=True)
    lvl_4 = models.CharField(max_length=500, blank=True, null=True)
    lvl_5 = models.CharField(max_length=500, blank=True, null=True)
    lvl_6 = models.CharField(max_length=500, blank=True, null=True)
    lvl_7 = models.CharField(max_length=500, blank=True, null=True)
    lvl_8 = models.CharField(max_length=500, blank=True, null=True)
    lvl_9 = models.CharField(max_length=500, blank=True, null=True)
    lvl_10 = models.CharField(max_length=500, blank=True, null=True)
    lvl_11 = models.CharField(max_length=500, blank=True, null=True)
    lvl_12 = models.CharField(max_length=500, blank=True, null=True)
    lvl_13 = models.CharField(max_length=500, blank=True, null=True)
    lvl_14 = models.CharField(max_length=500, blank=True, null=True)
    lvl_15 = models.CharField(max_length=500, blank=True, null=True)
    lvl_16 = models.CharField(max_length=500, blank=True, null=True)
    lvl_17 = models.CharField(max_length=500, blank=True, null=True)
    lvl_18 = models.CharField(max_length=500, blank=True, null=True)
    lvl_19 = models.CharField(max_length=500, blank=True, null=True)
    lvl_20 = models.CharField(max_length=500, blank=True, null=True)
    allowed_profiles = models.ManyToManyField(Profile,
                                              blank=True,
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='dead_player'),
                                              related_name='allowed_professions')

    class Meta:
        ordering = ['character_class', 'name']

    def __str__(self):
        return self.name

    def short_name(self):
        return ''.join(word[:4] for word in str(self.name).split(' '))
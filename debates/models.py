from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from PIL import Image
from users.models import Profile


class Topic(models.Model):
    title = models.CharField(max_length=50, unique=True, verbose_name='tytuł tematu')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=100, verbose_name='opis tematu')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_updated']


class Debate(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name='tytuł narady')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey(Topic, related_name='debates', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='debates', on_delete=models.CASCADE)
    allowed_profiles = models.ManyToManyField(to=Profile, related_name='allowed_debates',
                                              limit_choices_to=
                                              Q(character_status='active_player') |
                                              Q(character_status='inactive_player') |
                                              Q(character_status='living_npc'))
    is_ended = models.BooleanField(default=False)
    is_individual = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_updated']


class Remark(models.Model):
    text = models.TextField(max_length=4000)
    debate = models.ForeignKey(Debate, related_name='remarks', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='remarks', on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to='post_pics')

    def __str__(self):
        return self.text[:30]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

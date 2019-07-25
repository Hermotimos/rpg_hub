from django.db import models
from django.contrib.auth.models import User
from PIL import Image

STATUS = [
    ('active_player', 'Postać gracza'),
    ('inactive_player', 'Dawna postać gracza'),
    ('dead_player', 'Martwa postać gracza'),
    ('living_npc', 'Bohater niezależny'),
    ('dead_npc', 'Martwy bohater niezależny'),
    ('gm', 'Mistrz gry')
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default_profile.jpg', upload_to='profile_pics')
    character_name = models.CharField(max_length=50, default='')
    character_status = models.CharField(max_length=20, choices=STATUS, default='npc')

    def __str__(self):
        return f'{self.character_name}'

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    class Meta:
        ordering = ['character_status', 'character_name']


# maybe move to separate app ?
# class CharacterSheet(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     character_class = models.CharField(max_length=200, blank=True, null=True)
#     character_nickname = models.CharField(max_length=200, blank=True, null=True)


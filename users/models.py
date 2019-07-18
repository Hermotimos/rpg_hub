from django.db import models
from django.contrib.auth.models import User
from PIL import Image

STATUS = [
    ('active_player', 'Postać gracza'),
    ('inactive_player', 'Dawna postać gracza'),
    ('npc', 'Bohater niezależny'),
    ('gm', 'Mistrz gry')
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
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


# class CharacterSheet(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     character_class = models.CharField(max_length=200, blank=True, null=True)
#     character_nickname = models.CharField(max_length=200, blank=True, null=True)


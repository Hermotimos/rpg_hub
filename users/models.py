from django.db import models
from django.contrib.auth.models import User
from PIL import Image

STATUS = [
    # players
    ('active_player', 'Gracz'),
    ('inactive_player', 'Nieaktywny gracz'),
    ('dead_player', 'Martwy gracz'),
    # npc
    ('living_npc', 'Bohater niezależny'),
    ('dead_npc', 'Martwy bohater niezależny'),
    # other
    ('gm', 'Mistrz gry'),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/profile_default.jpg', upload_to='profile_pics')
    character_name = models.CharField(max_length=50, default='')
    character_status = models.CharField(max_length=20, choices=STATUS, default='living_npc')
    sorting_name = models.CharField(max_length=250, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        if self.user:
            if str(self.character_name)[0] == 'Ć':
                self.sorting_name = 'C' + str(self.character_name)
            elif str(self.character_name)[0] == 'Ł':
                self.sorting_name = 'L' + str(self.character_name)
            elif str(self.character_name)[0] == 'Ó':
                self.sorting_name = 'O' + str(self.character_name)
            elif str(self.character_name)[0] == 'Ś':
                self.sorting_name = 'S' + str(self.character_name)
            elif str(self.character_name)[0] == 'Ź':
                self.sorting_name = 'Z' + str(self.character_name)
            elif str(self.character_name)[0] == 'Ż':
                self.sorting_name = 'Z' + str(self.character_name)
            else:
                self.sorting_name = str(self.character_name)
            super(Profile, self).save(*args, **kwargs)

    class Meta:
        ordering = ['character_status', 'sorting_name']

    def __str__(self):
        return f'{self.character_name}'

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

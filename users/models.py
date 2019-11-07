from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    character_status = models.CharField(max_length=50, choices=STATUS, default='living_npc')

    class Meta:
        ordering = ['character_status', 'character_name']

    def __str__(self):
        return f'{self.character_name}'

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


@receiver(post_save, sender=User)                          # After a User is saved send signal 'post_save'
def create_profile(sender, instance, created, **kwargs):   # the receiver will be create_profile (via decoration)
    if created:                                            # if User has just been created (False for already existing)
        p = Profile.objects.create(user=instance)          # than create instance of Profile which is equal to User
        p.character_name = instance.username.replace('_', ' ')      # whose name will be the username without '_'
        p.save()                                                    # save Profile to save new character_name

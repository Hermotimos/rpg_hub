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
    ('living_npc', 'BN'),
    ('dead_npc', 'Martwy BN'),
    # other
    ('gm', 'MG'),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    character_name = models.CharField(max_length=50, default='')
    status = models.CharField(
        max_length=50,
        choices=STATUS,
        default='living_npc',
    )
    image = models.ImageField(
        default='profile_pics/profile_default.jpg',
        upload_to='profile_pics',
    )
    
    

    class Meta:
        ordering = ['status', 'character_name']

    def __str__(self):
        return f'{self.character_name or self.user.username}'
    
    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        p = Profile.objects.create(user=instance)
        p.character_name = instance.username.replace('_', ' ')
        p.save()

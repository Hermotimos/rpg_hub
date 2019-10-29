from django.db.models.signals import post_save
from django.contrib.auth.models import User         # sender of signal
from django.dispatch import receiver                # function to deal with signal
from users.models import Profile


@receiver(post_save, sender=User)                          # 1. When a User is saved, than send signal 'post_save'
def create_profile(sender, instance, created, **kwargs):   # 2. the receiver will be create_profile (via decoration)
    if created:                                            # 3. if User was created, than create instance of Profile
        Profile.objects.create(user=instance)              # ... which is equal to User


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

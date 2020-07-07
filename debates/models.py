import datetime
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.contrib.auth.models import User
from PIL import Image
from users.models import Profile


class Topic(models.Model):
    title = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Debate(models.Model):
    name = models.CharField(max_length=255, unique=True)
    topic = models.ForeignKey(
        to=Topic,
        related_name='debates',
        on_delete=models.CASCADE,
    )
    known_directly = models.ManyToManyField(
        to=Profile,
        related_name='debates_known_directly',
    )
    allowed_profiles = models.ManyToManyField(to=Profile,
                                              related_name='allowed_debates')
    # followers = models.ManyToManyField(
    #     to=Profile,
    #     related_name='followed_debates',
    #     blank=True,
    # )
    is_ended = models.BooleanField(default=False)
    is_individual = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    def informables(self):
        qs = Profile.objects.filter(status__in=[
            'active_player',
            'inactive_player',
        ])
        qs = qs.exclude(id__in=self.known_directly.all())
        return qs


class Remark(models.Model):
    text = models.TextField()
    debate = models.ForeignKey(
        to=Debate,
        related_name='remarks',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        to=User,
        related_name='remarks',
        on_delete=models.CASCADE,
    )
    seen_by = models.ManyToManyField(
        to=Profile,
        related_name='remarks_seen',
        blank=True,
    )
    image = models.ImageField(blank=True, null=True, upload_to='post_pics')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        text = self.text
        return f'{text[:100]}...' if len(str(text)) > 100 else text

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)


# -----------------------------------------------------------------------------
# ---------------------------------------- SIGNALS ----------------------------
# -----------------------------------------------------------------------------


def delete_if_doubled(sender, instance, **kwargs):
    time_span = instance.date_posted + datetime.timedelta(minutes=1)
    doubled = Remark.objects.filter(debate=instance.debate,
                                    text=instance.text,
                                    author=instance.author,
                                    date_posted__lt=time_span,  # TODO this doesnt work
                                    )

    if doubled.count() > 1:
        instance.delete()


post_save.connect(delete_if_doubled, sender=Remark)

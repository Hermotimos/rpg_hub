import datetime

from PIL import Image
from django.contrib.auth.models import User
from django.db.models import (
    BooleanField,
    CharField,
    CASCADE,
    DateTimeField,
    ForeignKey as FK,
    ImageField,
    ManyToManyField as M2MField,
    Model,
    Q,
    TextField,
)
from django.db.models.signals import post_save

from users.models import Profile

ALIVE_CHARACTERS = Q(status__in=[
    'active_player',
    'inactive_player',
    'living_npc',
])


class Topic(Model):
    title = CharField(max_length=255, unique=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Debate(Model):
    name = CharField(max_length=255, unique=True)
    topic = FK(to=Topic, related_name='debates', on_delete=CASCADE)
    known_directly = M2MField(
        to=Profile,
        related_name='debates_known_directly',
        limit_choices_to=ALIVE_CHARACTERS,
    )
    is_ended = BooleanField(default=False)
    is_individual = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)

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


class Remark(Model):
    text = TextField()
    debate = FK(to=Debate, related_name='remarks', on_delete=CASCADE)
    author = FK(to=User, related_name='remarks', on_delete=CASCADE)
    seen_by = M2MField(to=Profile, related_name='remarks_seen', blank=True)
    image = ImageField(blank=True, null=True, upload_to='post_pics')
    created_at = DateTimeField(auto_now_add=True)

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
    start = instance.created_at - datetime.timedelta(minutes=1)
    end = instance.created_at
    doubled = Remark.objects.filter(
        debate=instance.debate,
        text=instance.text,
        author=instance.author,
        created_at__range=[start, end],
    )
    if doubled.count() > 1:
        instance.delete()


post_save.connect(delete_if_doubled, sender=Remark)

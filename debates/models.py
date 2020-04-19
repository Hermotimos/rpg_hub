import datetime
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.contrib.auth.models import User
from PIL import Image
from users.models import Profile


class Topic(models.Model):
    title = models.CharField(max_length=100, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    allowed_profiles = models.ManyToManyField(to=Profile,
                                              related_name='allowed_topics',
                                              blank=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.title


class Debate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(to=Topic, related_name='debates',
                              on_delete=models.CASCADE)
    allowed_profiles = models.ManyToManyField(to=Profile,
                                              related_name='allowed_debates')
    followers = models.ManyToManyField(to=Profile,
                                       related_name='followed_debates',
                                       blank=True)
    is_ended = models.BooleanField(default=False)
    is_individual = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.name
    
    def informable(self):
        excluded = self.allowed_profiles.all()
        informable = Profile.objects.filter(
            status__in=['active_player', 'inactive_player']
        ).exclude(id__in=excluded)
        return informable


class Remark(models.Model):
    text = models.TextField(max_length=4000)
    debate = models.ForeignKey(to=Debate, related_name='remarks',
                               on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(to=User, related_name='remarks',
                               on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to='post_pics')
    seen_by = models.ManyToManyField(to=Profile,
                                     related_name='remarks_seen',
                                     blank=True)

    def __str__(self):
        text = self.text
        return f'{text[:100]}...' if len(str(text)) > 100 else text

    def text_begin(self):
        return self.__str__()

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


def update_topic_allowed_profiles(sender, instance, **kwargs):
    topic = instance.topic
    allowed = [profile for profile in instance.allowed_profiles.all()]
    topic.allowed_profiles.add(*allowed)
    topic.save()


post_save.connect(update_topic_allowed_profiles, sender=Debate)
m2m_changed.connect(update_topic_allowed_profiles,
                    sender=Debate.allowed_profiles.through)


def delete_if_doubled(sender, instance, **kwargs):
    time_span = datetime.datetime.now() - datetime.timedelta(minutes=5)
    doubled = Remark.objects.filter(text=instance.text, author=instance.author,
                                    date_posted__gte=time_span)
    if doubled.count() > 1:
        instance.delete()


post_save.connect(delete_if_doubled, sender=Remark)

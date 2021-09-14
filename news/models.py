import datetime

from PIL import Image
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey as FK,
    ImageField,
    Manager,
    ManyToManyField as M2M,
    Model,
    TextField,
)
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Profile


class News(Model):
    title = CharField(max_length=100, unique=True)
    text = TextField(max_length=4000)
    created_at = DateTimeField(auto_now_add=True)
    author = FK(to=Profile, related_name='news_authored', on_delete=CASCADE)
    allowed_profiles = M2M(to=Profile, related_name='allowed_news')
    followers = M2M(to=Profile, related_name='followed_news', blank=True)
    image = ImageField(blank=True, null=True, upload_to='news_pics')
    seen_by = M2M(to=Profile, related_name='news_seen', blank=True)

    def __str__(self):
        return self.title[:50] + '...' if len(str(self.title)) > 100 else self.title

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'


class NewsAnswer(Model):
    news = FK(to=News, related_name='news_answers', on_delete=CASCADE)
    author = FK(to=Profile, related_name='news_answers', on_delete=CASCADE)
    text = TextField(max_length=4000)
    created_at = DateTimeField(auto_now_add=True)
    image = ImageField(blank=True, null=True, upload_to='news_pics')
    seen_by = M2M(to=Profile, related_name='news_answers_seen', blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.text[:100] + '...' if len(str(self.text)) > 100 else self.text

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)


class Survey(Model):
    title = CharField(max_length=100, unique=True)
    author = FK(to=Profile, related_name='surveys_authored', on_delete=CASCADE)
    text = TextField(max_length=4000)
    image = ImageField(blank=True, null=True, upload_to='news_pics')
    created_at = DateTimeField(auto_now_add=True)
    addressees = M2M(to=Profile, related_name='surveys_received')
    seen_by = M2M(to=Profile, related_name='surveys_seen', blank=True)

    def __str__(self):
        return self.title[:50] + '...' if len(str(self.title)) > 50 else self.title

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)


class SurveyOptionManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('no_voters', 'yes_voters')
        return qs
    
    
class SurveyOption(Model):
    objects = SurveyOptionManager()
    
    survey = FK(to=Survey, related_name='survey_options', on_delete=CASCADE)
    author = FK(to=Profile, related_name='survey_options_authored', on_delete=CASCADE)
    option_text = CharField(max_length=50)
    yes_voters = M2M(to=Profile, related_name='survey_yes_votes', blank=True)
    no_voters = M2M(to=Profile, related_name='survey_no_votes', blank=True)

    class Meta:
        ordering = ['option_text']

    def __str__(self):
        return self.option_text[:100] + '...' if len(str(self.option_text)) > 100 else self.option_text


class SurveyAnswer(Model):
    survey = FK(to=Survey, related_name='survey_answers', on_delete=CASCADE)
    author = FK(to=Profile, related_name='survey_answers', on_delete=CASCADE)
    text = TextField(max_length=4000)
    created_at = DateTimeField(auto_now_add=True)
    image = ImageField(blank=True, null=True, upload_to='news_pics')
    seen_by = M2M(to=Profile, related_name='survey_answers_seen', blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.text[:100] + '...' if len(str(self.text)) > 100 else self.text

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
# ---------------------------------- SIGNALS ----------------------------------
# -----------------------------------------------------------------------------


@receiver(post_save, sender=NewsAnswer)
@receiver(post_save, sender=SurveyAnswer)
def delete_if_doubled(sender, instance, **kwargs):
    time_span = datetime.datetime.now() - datetime.timedelta(minutes=2)
    doubled = 0
    if isinstance(instance, NewsAnswer):
        doubled = NewsAnswer.objects.filter(text=instance.text, author=instance.author, created_at__gte=time_span)
    elif isinstance(instance, SurveyAnswer):
        doubled = SurveyAnswer.objects.filter(text=instance.text, author=instance.author, created_at__gte=time_span)
    if doubled.count() > 1:
        instance.delete()

import datetime
from PIL import Image

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Profile


class News(models.Model):
    title = models.CharField(max_length=100, unique=True)
    text = models.TextField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='news', on_delete=models.CASCADE)
    allowed_profiles = models.ManyToManyField(Profile, related_name='allowed_news')
    followers = models.ManyToManyField(Profile, related_name='followed_news', blank=True)
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')
    seen_by = models.ManyToManyField(Profile, related_name='news_seen', blank=True)

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
        ordering = ['-created_at']
        verbose_name = 'News'
        verbose_name_plural = 'News'


class NewsAnswer(models.Model):
    news = models.ForeignKey(News, related_name='news_answers', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='news_answers', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')
    seen_by = models.ManyToManyField(Profile, related_name='news_answers_seen', blank=True)

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


class Survey(models.Model):
    title = models.CharField(max_length=100, unique=True)
    author = models.ForeignKey(User, related_name='surveys_authored', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')
    created_at = models.DateTimeField(auto_now_add=True)
    addressees = models.ManyToManyField(Profile, related_name='surveys_received')
    seen_by = models.ManyToManyField(Profile, related_name='surveys_seen', blank=True)

    class Meta:
        ordering = ['-created_at']

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


class SurveyOption(models.Model):
    survey = models.ForeignKey(Survey, related_name='survey_options', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='survey_options_authored', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=50)
    yes_voters = models.ManyToManyField(Profile, related_name='survey_yes_votes', blank=True)
    no_voters = models.ManyToManyField(Profile, related_name='survey_no_votes', blank=True)

    class Meta:
        ordering = ['option_text']

    def __str__(self):
        return self.option_text[:100] + '...' if len(str(self.option_text)) > 100 else self.option_text


class SurveyAnswer(models.Model):
    survey = models.ForeignKey(Survey, related_name='survey_answers', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='survey_answers', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')
    seen_by = models.ManyToManyField(Profile, related_name='survey_answers_seen', blank=True)

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


# ---------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- SIGNALS ---------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


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

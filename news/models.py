from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
from users.models import Profile
from PIL import Image


class News(models.Model):
    title = models.CharField(max_length=100, unique=True)
    text = models.TextField(max_length=4000)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='news', on_delete=models.CASCADE)
    allowed_profiles = models.ManyToManyField(Profile, related_name='allowed_news')
    followers = models.ManyToManyField(Profile, related_name='followed_news', blank=True)
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')

    def __str__(self):
        return self.title[:50] + '...' if len(str(self.title)) > 100 else self.title

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

    class Meta:
        ordering = ['-date_posted']
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def last_activity(self):
        return self.news_answers.all().aggregate(Max('date_posted'))['date_posted__max']


class NewsAnswer(models.Model):
    news = models.ForeignKey(News, related_name='news_answers', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='news_answers', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    date_posted = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')

    class Meta:
        ordering = ['date_posted']

    def __str__(self):
        return self.text[:100] + '...' if len(str(self.text)) > 100 else self.text

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
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
    date_posted = models.DateTimeField(auto_now_add=True)
    addressees = models.ManyToManyField(Profile, related_name='surveys_received')
    seen_by = models.ManyToManyField(Profile, related_name='surveys_seen', blank=True)

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return self.title[:50] + '...' if len(str(self.title)) > 50 else self.title

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
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
    date_posted = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')

    class Meta:
        ordering = ['date_posted']

    def __str__(self):
        return self.text[:100] + '...' if len(str(self.text)) > 100 else self.text

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

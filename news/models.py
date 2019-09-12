from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
from users.models import Profile
from PIL import Image


class News(models.Model):
    title = models.CharField(max_length=100, unique=True)
    text = models.TextField(max_length=4000)
    date_posted = models.DateTimeField(auto_now_add=True)
    # date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, related_name='news', on_delete=models.CASCADE)
    allowed_profiles = models.ManyToManyField(to=Profile, related_name='allowed_news')
    followers = models.ManyToManyField(to=Profile, related_name='followed_news', blank=True)
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')

    def __str__(self):
        return self.title[:50] + '...'

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
        return self.text[:100] + '...'

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (700, 700)
                img.thumbnail(output_size)
                img.save(self.image.path)

from django.urls import reverse
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from users.models import Profile
from PIL import Image


PLAYERS = [(profile.user.username, profile.user.username)
           for profile in Profile.objects.filter(character_status='player')]


class News(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    text = models.TextField(max_length=4000)
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, related_name='news', on_delete=models.CASCADE)
    allowed_profiles = models.ManyToManyField(to=Profile, related_name='allowed_news')
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')

    def __str__(self):
        return self.title[:50] + '...'

    def _get_unique_slug(self):
        slug = slugify(self.title)
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, *kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path)

    def get_absolute_url(self):
        # return f'/news/{self.slug}'                                    # one way
        return reverse('news-detail', kwargs={'news_slug': self.slug})   # another way

    class Meta:
        ordering = ['-date_updated']


class Response(models.Model):
    text = models.TextField(max_length=4000)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='responses', on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to='news_pics')
    news = models.ForeignKey(News, related_name='responses', on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        super().save(*args, *kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path)

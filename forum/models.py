from django.urls import reverse
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from PIL import Image
from users.models import Profile


class Board(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def _get_unique_slug(self):
        slug = slugify(self.title)
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, *kwargs)

    class Meta:
        ordering = ['-date_updated']


class Topic(models.Model):
    USERS = [(profile.character_name, profile.character_name) for profile in Profile.objects.all()]

    topic_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    board = models.ForeignKey(Board, related_name='topics', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    allowed_users = MultiSelectField(max_length=100, choices=USERS, default='MG')
    allowed_profiles = models.ManyToManyField(to=Profile, related_name='allowed_topics')

    def __str__(self):
        return self.topic_name

    def _get_unique_slug(self):
        slug = slugify(self.topic_name)
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, *kwargs)

    def get_absolute_url(self):
        # return f'/forum/{self.board.slug}/{self.slug}'                                            # one way
        return reverse('topic', kwargs={'board_slug': self.board.slug, 'topic_slug': self.slug})    # another way

    class Meta:
        ordering = ['-date_updated']


class Post(models.Model):
    text = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to='post_pics')

    def __str__(self):
        return self.text[:30]

    def save(self, *args, **kwargs):
        super().save()

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 700 or img.width > 700:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path)

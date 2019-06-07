from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from multiselectfield import MultiSelectField       # pip install django-multiselectfield


STATUS = (
    (0, 'Awaiting'),
    (1, 'Approved')
)

USERS = [(user.username, user.username) for user in User.objects.all()]


class Board(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
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


class Topic(models.Model):
    topic_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    board = models.ForeignKey(Board, related_name='topics', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    allowed_users = MultiSelectField(max_length=100, choices=USERS)

    def __str__(self):
        return self.topic_name

    def _get_unique_slug(self):
        slug = slugify(self.topic_name)
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, *kwargs)


class Post(models.Model):
    text = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)

    def __str__(self):
        return self.text[:30]

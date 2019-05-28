from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    # allowed_users = TODO ??????????????

    def __str__(self):
        return self.name


class Topic(models.Model):
    topic_name = models.CharField(max_length=255, unique=True)
    last_updated = models.DateTimeField(auto_now=True)
    board = models.ForeignKey(Board, related_name='topics', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)

    def __str__(self):
        return self.topic_name


class Post(models.Model):
    text = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    rpg_time = models.CharField(max_length=100)

    def __str__(self):
        return self.text[:30]

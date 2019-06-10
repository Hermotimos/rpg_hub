from django.db import models
from django.contrib.auth.models import User
from users.models import Profile
from multiselectfield import MultiSelectField

PLAYERS = [(player.user.username, player.user.username) for player in Profile.objects.filter(character_status='player')]


class News(models.Model):
    title = models.CharField(max_length=100, unique=True)
    text = models.TextField(max_length=4000)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='news', on_delete=models.CASCADE)
    allowed_users = MultiSelectField(max_length=100, choices=PLAYERS)

    def __str__(self):
        return self.title[:50] + '...'

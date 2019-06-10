from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

USERS = [(user.username, user.username) for user in User.objects.all()]


class News(models.Model):
    text = models.TextField(max_length=4000)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='news', on_delete=models.CASCADE)
    allowed_users = MultiSelectField(max_length=100, choices=USERS)

    def __str__(self):
        return self.text[:30]

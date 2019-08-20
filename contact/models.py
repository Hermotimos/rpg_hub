from django.db import models
from users.models import User


class Report(models.Model):
    author = models.ForeignKey(User, related_name='reports', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    date_created = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)
    response = models.TextField(max_length=4000, blank=True, null=True)

    def __str__(self):
        return f'{self.text[0:50]}...'

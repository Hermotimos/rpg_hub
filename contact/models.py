from django.db import models
from users.models import User


class Demand(models.Model):
    author = models.ForeignKey(User, related_name='reports', on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    date_created = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)
    response = models.TextField(max_length=4000, blank=True, null=True)

    def __str__(self):
        return f'{self.text[0:50]}...'


# class Response(models.Model):
#     report = models.ForeignKey(Demand, related_name='responses', on_delete=models.CASCADE)
#     response = models.TextField(max_length=4000, blank=True, null=True)
#     author = models.ForeignKey(User, related_name='responses', on_delete=models.CASCADE)
#     text = models.TextField(max_length=4000)
#     date_posted = models.DateTimeField(auto_now_add=True)
#     image = models.ImageField(blank=True, null=True, upload_to='news_pics')



from django.urls import path
from timeline.views import timeline_view


urlpatterns = [
    path('', timeline_view, name='timeline')
]

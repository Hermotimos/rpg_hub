from django.urls import path
from timeline.views import timeline_view, create_event_view


urlpatterns = [
    path('', timeline_view, name='timeline'),
    path('create-event/', create_event_view, name='create-event')
]

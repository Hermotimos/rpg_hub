from django.urls import path
from timeline.views import timeline_view, timeline__filtered_view


urlpatterns = [
    path('', timeline_view, name='timeline')
]

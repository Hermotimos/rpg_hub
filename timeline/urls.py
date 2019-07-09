from django.urls import path
from timeline.views import timeline_view


urlpatterns = [
    path('create_board/', timeline_view, name='timeline')
]
from django.urls import path
from timeline.views import timeline_view, create_event_view, event_add_informed_view


urlpatterns = [
    path('', timeline_view, name='timeline'),
    path('create-event/', create_event_view, name='create_event'),
    path('<int:event_id>/event-add-informed/', event_add_informed_view, name='add_informed')
]

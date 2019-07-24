from django.urls import path
from timeline.views import timeline_view, create_event_view, edit_event_view, event_add_informed_view, \
    event_note_view, chronicles_all_view


urlpatterns = [
    path('', timeline_view, name='timeline'),
    path('create-event/', create_event_view, name='create_event'),
    path('<int:event_id>/edit-event/', edit_event_view, name='edit_event'),
    path('<int:event_id>/event-add-informed/', event_add_informed_view, name='add_informed'),
    path('<int:event_id>/event-note/', event_note_view, name='event_note'),
    path('chronicles_all/', chronicles_all_view, name='chronicles-all'),
]

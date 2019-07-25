from django.urls import path
from timeline.views import timeline_view, create_event_view, edit_event_view, event_add_informed_view, \
    event_note_view, described_event_note_view, chronicles_chapters_view, chronicles_all_view, \
    chronicles_one_chapter_view


urlpatterns = [
    path('', timeline_view, name='timeline'),
    path('create-event/', create_event_view, name='create_event'),
    path('<int:event_id>/edit-event/', edit_event_view, name='edit_event'),
    path('<int:event_id>/event-add-informed/', event_add_informed_view, name='add_informed'),
    path('<int:event_id>/event-note/', event_note_view, name='event_note'),
    path('<int:event_id>/described-event-note/', described_event_note_view, name='described_event_note'),
    path('chronicles_chapters/chronicles_all/', chronicles_all_view, name='chronicles_all'),
    path('chronicles_chapters/', chronicles_chapters_view, name='chronicles_chapters'),
    path('chronicles_chapters/<int:game_no>/chapter/', chronicles_one_chapter_view, name='chronicles_one_chapter'),
]

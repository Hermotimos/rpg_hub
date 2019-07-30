from django.urls import path
from timeline.views import *


urlpatterns = [
    path('', timeline_main_view, name='timeline-main'),
    path('timeline-events/', timeline_events_view, name='timeline-events'),
    path('timeline-by-thread/<int:thread_id>/', timeline_by_thread_view, name='timeline-by-thread'),
    path('timeline-by-participant/<int:participant_id>/', timeline_by_participant_view, name='timeline-by-participant'),
    path('timeline-by-general-location/<int:general_location_id>/', timeline_by_general_location_view, name='timeline-by-general-location'),
    path('timeline-by-specific-location/<int:specific_location_id>/', timeline_by_specific_location_view, name='timeline-by-specific-location'),
    path('timeline-by-year/<int:year>/', timeline_by_year_view, name='timeline-by-year'),

    path('create-event/', create_event_view, name='create-event'),
    path('<int:event_id>/event-add-informed/', event_add_informed_view, name='add-informed'),
    path('<int:event_id>/event-note/', event_note_view, name='event-note'),
    path('<int:event_id>/edit-event/', edit_event_view, name='edit-event'),


    path('chronicles_chapters/', chronicles_chapters_view, name='chronicles-chapters'),
    path('chronicles_chapters/chronicles_all/', chronicles_all_view, name='chronicles-all'),
    path('chronicles_chapters/<int:game_id>/chapter/', chronicles_one_chapter_view, name='chronicles-one-chapter'),

    path('create-described-event/', create_described_event_view, name='create-described-event'),
    path('<int:event_id>/described-event-add-informed/', described_event_add_informed_view, name='described-event-add-informed'),
    path('<int:event_id>/described-event-note/', described_event_note_view, name='described-event-note'),
    path('<int:event_id>/edit-described-event/', edit_described_event_view, name='edit-described-event'),
]

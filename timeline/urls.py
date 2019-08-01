from django.urls import path
from timeline.views import timeline_main_view, timeline_events_view, timeline_by_thread_view, \
    timeline_by_participant_view, timeline_by_general_location_view, timeline_by_specific_location_view, \
    timeline_by_year_view, create_event_view, edit_event_view, event_add_informed_view, \
    event_note_view, described_event_note_view, chronicles_chapters_view, chronicles_all_view, \
    chronicles_one_chapter_view, create_described_event_view, described_event_add_informed_view,\
    edit_described_event_view


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


    path('chronicles/', chronicles_chapters_view, name='chronicles-chapters'),
    path('chronicles/all_chapters/', chronicles_all_view, name='chronicles-all'),
    path('chronicles/chapter<int:game_id>/', chronicles_one_chapter_view, name='chronicles-one-chapter'),

    path('chronicles/create-described-event/', create_described_event_view, name='create-described-event'),
    path('chronicles/<int:event_id>/described-event-add-informed/', described_event_add_informed_view, name='described-event-add-informed'),
    path('chronicles/<int:event_id>/described-event-note/', described_event_note_view, name='described-event-note'),
    path('chronicles/<int:event_id>/edit-described-event/', edit_described_event_view, name='edit-described-event'),
]

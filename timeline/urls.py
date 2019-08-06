from django.urls import path
from timeline import views


urlpatterns = [
    path('', views.timeline_main_view, name='timeline-main'),
    path('timeline-events/', views.timeline_events_view, name='timeline-events'),
    path('timeline-by-thread/<int:thread_id>/', views.timeline_by_thread_view, name='timeline-by-thread'),
    path('timeline-by-participant/<int:participant_id>/', views.timeline_by_participant_view, name='timeline-by-participant'),
    path('timeline-by-general-location/<int:general_location_id>/', views.timeline_by_general_location_view, name='timeline-by-general-location'),
    path('timeline-by-specific-location/<int:specific_location_id>/', views.timeline_by_specific_location_view, name='timeline-by-specific-location'),
    path('timeline-by-year-and-season/<int:year>/<str:season>/', views.timeline_by_year_and_season_view, name='timeline-by-year-and-season'),

    path('create-event/', views.create_event_view, name='create-event'),
    path('<int:event_id>/event-add-informed/', views.event_add_informed_view, name='add-informed'),
    path('<int:event_id>/event-note/', views.event_note_view, name='event-note'),
    path('<int:event_id>/edit-event/', views.edit_event_view, name='edit-event'),


    path('chronicles/', views.chronicles_chapters_view, name='chronicles-chapters'),
    path('chronicles/all_chapters/', views.chronicles_all_view, name='chronicles-all'),
    path('chronicles/chapter<int:game_id>/', views.chronicles_one_chapter_view, name='chronicles-one-chapter'),

    path('chronicles/create-described-event/', views.create_described_event_view, name='create-described-event'),
    path('chronicles/<int:event_id>/described-event-add-informed/', views.described_event_add_informed_view, name='described-event-add-informed'),
    path('chronicles/<int:event_id>/described-event-note/', views.described_event_note_view, name='described-event-note'),
    path('chronicles/<int:event_id>/edit-described-event/', views.edit_described_event_view, name='edit-described-event'),
]

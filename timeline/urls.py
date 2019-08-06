from django.urls import path
from timeline import views


urlpatterns = [

    # timeline
    path('timeline', views.timeline_main_view, name='timeline-main'),
    path('timeline/events/', views.timeline_events_view, name='timeline-events'),
    path('timeline/by-thread/<int:thread_id>/', views.timeline_by_thread_view, name='timeline-by-thread'),
    path('timeline/by-participant/<int:participant_id>/', views.timeline_by_participant_view, name='timeline-by-participant'),
    path('timeline/by-general-location/<int:general_location_id>/', views.timeline_by_general_location_view, name='timeline-by-general-location'),
    path('timeline/by-specific-location/<int:specific_location_id>/', views.timeline_by_specific_location_view, name='timeline-by-specific-location'),
    path('timeline/by-year-and-season/<int:year>/<str:season>/', views.timeline_by_year_and_season_view, name='timeline-by-year-and-season'),

    path('timeline/create/', views.create_event_view, name='create-event'),
    path('timeline/<int:event_id>/add-informed/', views.event_add_informed_view, name='add-informed'),
    path('timeline/<int:event_id>/note/', views.event_note_view, name='event-note'),
    path('timeline/<int:event_id>/edit/', views.edit_event_view, name='edit-event'),

    # chronicle
    path('chronicle/', views.chronicles_chapters_view, name='chronicle-chapters'),
    path('chronicle/all_chapters/', views.chronicles_all_view, name='chronicle-chapters-all'),
    path('chronicle/chapter<int:game_id>/', views.chronicles_one_chapter_view, name='chronicle-chapter'),

    path('chronicle/create/', views.create_described_event_view, name='create-described-event'),
    path('chronicle/<int:event_id>/add-informed/', views.described_event_add_informed_view, name='described-event-add-informed'),
    path('chronicle/<int:event_id>/note/', views.described_event_note_view, name='described-event-note'),
    path('chronicle/<int:event_id>/edit/', views.edit_described_event_view, name='edit-described-event'),
]

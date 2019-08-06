from django.urls import path
from history import views


urlpatterns = [

    # timeline
    path('timeline', views.timeline_main_view, name='timeline-main'),
    path('timeline/events/', views.timeline_events_view, name='timeline-events'),
    path('timeline/by-thread:<int:thread_id>/', views.timeline_by_thread_view, name='timeline-by-thread'),
    path('timeline/by-participant:<int:participant_id>/', views.timeline_by_participant_view, name='timeline-by-participant'),
    path('timeline/by-general-location:<int:general_location_id>/', views.timeline_by_general_location_view, name='timeline-by-general-location'),
    path('timeline/by-specific-location:<int:specific_location_id>/', views.timeline_by_specific_location_view, name='timeline-by-specific-location'),
    path('timeline/by-year-and-season:<int:year>/<str:season>/', views.timeline_by_year_and_season_view, name='timeline-by-year-and-season'),
    path('timeline/create/', views.create_event_view, name='timeline-create'),
    path('timeline/inform:<int:event_id>/', views.event_add_informed_view, name='timeline-inform'),
    path('timeline/note:<int:event_id>/', views.event_note_view, name='timeline-note'),
    path('timeline/edit:<int:event_id>/', views.edit_event_view, name='timeline-edit'),

    # chronicle
    path('chronicle/', views.chronicles_chapters_view, name='chronicle-main'),
    path('chronicle/chapters-all/', views.chronicles_all_view, name='chronicle-chapters-all'),
    path('chronicle/chapter:<int:game_id>/', views.chronicles_one_chapter_view, name='chronicle-chapter'),
    path('chronicle/create/', views.create_described_event_view, name='chronicle-create'),
    path('chronicle/inform:<int:event_id>/', views.described_event_add_informed_view, name='chronicle-inform'),
    path('chronicle/note:<int:event_id>/', views.described_event_note_view, name='chronicle-note'),
    path('chronicle/edit:<int:event_id>/', views.edit_described_event_view, name='chronicle-edit'),
]

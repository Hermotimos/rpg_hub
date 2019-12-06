from django.urls import path
from history import views


app_name = 'history'
urlpatterns = [
    # chronicle
    path('chronicle/', views.chronicle_main_view, name='chronicle-main'),
    path('chronicle/create/', views.chronicle_create_view, name='chronicle-create'),
    path('chronicle/all-chapters/', views.chronicle_all_chapters_view, name='chronicle-all-chapters'),
    path('chronicle/one-chapter:<int:chapter_id>/', views.chronicle_one_chapter_view, name='chronicle-one-chapter'),
    path('chronicle/one-game:<int:game_id>:<timeline_event_id>/', views.chronicle_one_game_view, name='chronicle-one-game'),
    path('chronicle/inform:<int:event_id>/', views.chronicle_inform_view, name='chronicle-inform'),
    path('chronicle/note:<int:event_id>/', views.chronicle_note_view, name='chronicle-note'),
    path('chronicle/edit:<int:event_id>/', views.chronicle_edit_view, name='chronicle-edit'),
    path('chronicle/gap:<int:timeline_event_id>/', views.chronicle_gap_view, name='chronicle-gap'),
    # timeline
    path('timeline/', views.timeline_main_view, name='timeline-main'),
    path('timeline/create/', views.timeline_create_view, name='timeline-create'),
    path('timeline/all-events/', views.timeline_all_events_view, name='timeline-all-events'),
    path('timeline/thread:<int:thread_id>/', views.timeline_thread_view, name='timeline-thread'),
    path('timeline/participant:<int:participant_id>/', views.timeline_participant_view, name='timeline-participant'),
    path('timeline/gen-loc:<int:gen_loc_id>/', views.timeline_general_location_view, name='timeline-gen-loc'),
    path('timeline/spec-loc:<int:spec_loc_id>/', views.timeline_specific_location_view, name='timeline-spec-loc'),
    path('timeline/date:<int:year>:<str:season>/', views.timeline_date_view, name='timeline-date'),
    path('timeline/game:<int:game_id>/', views.timeline_game_view, name='timeline-game'),
    path('timeline/inform:<int:event_id>/', views.timeline_inform_view, name='timeline-inform'),
    path('timeline/note:<int:event_id>/', views.timeline_note_view, name='timeline-note'),
    path('timeline/edit:<int:event_id>/', views.timeline_edit_view, name='timeline-edit'),

]

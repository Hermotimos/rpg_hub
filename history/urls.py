from django.urls import path
from history import views


app_name = 'history'
urlpatterns = [
    # chronicle
    path('chronicle/', views.chronicle_main_view, name='chronicle-main'),
    path('chronicle/all-chapters/', views.chronicle_all_chapters_view, name='chronicle-all-chapters'),
    path('chronicle/one-chapter:<int:chapter_id>/', views.chronicle_one_chapter_view, name='chronicle-one-chapter'),
    path('chronicle/one-game:<int:game_id>:<timeline_event_id>/', views.chronicle_one_game_view, name='chronicle-one-game'),
    path('chronicle/inform:<int:event_id>/', views.chronicle_inform_view, name='chronicle-inform'),
    path('chronicle/gap:<int:timeline_event_id>/', views.chronicle_gap_view, name='chronicle-gap'),
    # timeline
    path('timeline/', views.timeline_main_view, name='timeline-main'),
    path('timeline/'
         'thread:<int:thread_id>/'
         'participant:<int:participant_id>/'
         'gen-loc:<int:gen_loc_id>/'
         'spec-loc:<int:spec_loc_id>/'
         'date:<int:year>:<str:season>/'
         'game:<int:game_id>/',
         views.timeline_filter_events_view, name='timeline-events'),

    path('timeline/inform:<int:event_id>/', views.timeline_inform_view, name='timeline-inform'),
]

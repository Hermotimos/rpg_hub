from django.urls import path
from chronicles import views


app_name = 'chronicles'
urlpatterns = [
    # chronicle
    path('chronicle/main/', views.chronicle_main_view, name='chronicle-main'),
    path('chronicle/all/', views.chronicle_all_view, name='chronicle-all'),
    path('chronicle/game:<int:game_id>/', views.chronicle_game_view,
         name='chronicle-game'),
    path('chronicle/chapter:<int:chapter_id>/', views.chronicle_chapter_view,
         name='chronicle-chapter'),
    path('inform/game-event:<int:game_event_id>/',
         views.game_event_inform_view, name='game-event-inform'),
    
    # timeline
    path('timeline/', views.timeline_view, name='timeline'),
    path('chronologies/', views.chronologies_view, name='chronologies'),
]

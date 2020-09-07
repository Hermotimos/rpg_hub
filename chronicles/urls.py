from django.urls import path
from chronicles import views_recreate
from chronicles import views

app_name = 'chronicles'
urlpatterns = [
    # path('', views_recreate.recreate, name='recreate'),
    path('mig/', views_recreate.migrate_debates, name='migrate-debates'),
    
    # chronicle
    path('chronicle/contents/', views.chronicle_contents_view,
         name='chronicle-contents'),
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

from django.urls import include, path

from chronicles import views


app_name = 'chronicles'
urlpatterns = [

    path(
        'chronicle/',
        include(
            [
                path('main/', views.chronicle_main_view, name='chronicle-main'),
                path('all/', views.chronicle_all_view, name='chronicle-all'),
                path('game:<int:game_id>/', views.chronicle_game_view, name='chronicle-game'),
                path('chapter:<int:chapter_id>/', views.chronicle_chapter_view, name='chronicle-chapter'),
            ]
        )
    ),

    path('inform/game-event:<int:game_event_id>/',
         views.game_event_inform_view, name='game-event-inform'),

    # timeline
    path('timeline/', views.timeline_view, name='timeline'),
    path('chronologies/', views.chronologies_view, name='chronologies'),
]

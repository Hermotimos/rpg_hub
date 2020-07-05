from django.urls import path
from chronicles import views_recreate
from chronicles import views

app_name = 'chronicles'
urlpatterns = [
    path('', views_recreate.recreate, name='recreate'),
    # chronicle
    path('chronicle/contents/', views.chronicle_contents_view,
         name='chronicle-contents'),
    path('chronicle/all/', views.chronicle_all_view, name='chronicle-all'),
    path('chronicle/game:<str:game_title>/', views.chronicle_game_view,
         name='chronicle-game'),
    path('chronicle/chapter:<str:chapter_title>/', views.chronicle_chapter_view,
         name='chronicle-chapter'),

]

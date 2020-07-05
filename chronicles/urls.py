from django.urls import path
from chronicles import views_recreate
from chronicles import views

app_name = 'chronicles'
urlpatterns = [
    path('', views_recreate.recreate, name='recreate'),
    
    path('contents/', views.chronicle_content_view, name='chronicle-content'),
    path('game:<str:game_title>/', views.game_view, name='game'),
    path('chapter:<str:chapter_title>/', views.chapter_view, name='chapter'),
    path('all-chapters/', views.all_chapters_view, name='all-chapters'),

]

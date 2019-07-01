from django.urls import path
from . import views


urlpatterns = [
    path('', views.forum_view, name='forum'),
    path('create_board/', views.create_board_view, name='create_board'),
    path('<slug:board_slug>/create_topic/', views.create_topic_view, name='create_topic'),
    path('<slug:board_slug>/<slug:topic_slug>/', views.posts_in_topic_view, name='topic'),
    path('<slug:board_slug>/<slug:topic_slug>/update_topic/', views.add_allowed_profiles_view, name='update_topic')
]
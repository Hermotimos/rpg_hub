from django.urls import path
from forum import views


urlpatterns = [
    path('', views.forum_view, name='forum'),
    path('create_board/', views.create_board_view, name='create-board'),
    path('<slug:board_slug>/create_topic/', views.create_topic_view, name='create-topic'),
    path('<slug:board_slug>/<slug:topic_slug>/', views.topic_view, name='topic'),
    path('<slug:board_slug>/<slug:topic_slug>/update_topic/', views.add_allowed_profiles_view, name='update-topic')
]
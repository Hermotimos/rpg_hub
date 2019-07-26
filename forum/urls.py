from django.urls import path
from forum.views import forum_view, create_board_view, create_topic_view, topic_view, add_allowed_profiles_view


urlpatterns = [
    path('', forum_view, name='forum'),
    path('create_board/', create_board_view, name='create_board'),
    path('<slug:board_slug>/create_topic/', create_topic_view, name='create_topic'),
    path('<slug:board_slug>/<slug:topic_slug>/', topic_view, name='topic'),
    path('<slug:board_slug>/<slug:topic_slug>/update_topic/', add_allowed_profiles_view, name='update_topic')
]
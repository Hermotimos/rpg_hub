from django.urls import path
from debates import views


app_name = 'debates'
urlpatterns = [
    path('', views.debates_main_view, name='main'),
    path('create-topic/', views.create_topic_view, name='create-topic'),
    path('topic:<int:topic_id>/create-debate/', views.create_debate_view, name='create-debate'),
    path('topic:<int:topic_id>/debate:<int:debate_id>/', views.debate_view, name='debate'),
    # path('topic:<int:topic_id>/debate:<int:debate_id>/invite/', views.debates_invite_view, name='invite'),
    path('topic:<int:topic_id>/debate:<int:debate_id>/unfollow/', views.unfollow_debate_view, name='unfollow'),
    path('topic:<int:topic_id>/debate:<int:debate_id>/follow/', views.follow_debate_view, name='follow'),
]

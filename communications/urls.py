from django.urls import path
from communications import views


app_name = 'communications'
urlpatterns = [
    # announcements
    path('announcements/', views.announcements_view, name='announcements'),
    path('thread:<int:thread_id>/', views.thread_view, name='thread'),
    path('thread:<int:thread_id>/unfollow', views.unfollow_thread_view,
         name='unfollow'),
    path('thread:<int:thread_id>/follow', views.follow_thread_view,
         name='follow'),
    
    path('create-topic:<str:thread_kind>/', views.create_topic_view, name='create-topic'),
    path('create-thread:<str:thread_kind>/', views.create_thread_view, name='create-thread'),
    
    # news
    
    # path('news-detail:<int:news_id>/follow', views.follow_news_view, name='follow'),
    
    # survey
    # path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/yes', views.vote_yes_view, name='survey-yes'),
    # path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/no', views.vote_no_view, name='survey-no'),
    # path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/unvote', views.unvote_view, name='survey-unvote'),
    # path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/modify', views.survey_option_modify_view,
    #      name='survey-option-modify'),
    # path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/delete', views.survey_option_delete_view,
    #      name='survey-option-delete'),
]

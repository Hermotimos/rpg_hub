from django.urls import path
from communications import views


app_name = 'communications'
urlpatterns = [
    # announcements
    path('announcements/', views.announcements_view, name='announcements'),
    path('announcement:<int:announcement_id>/', views.announcement_view,
         name='announcement'),
    
    # news
    # path('news-topic-create/', views.create_topic_view, name='topic-create'),
    # path('news-news-create/', views.create_news_view, name='news-create'),
    
    # path('news-detail:<int:news_id>/unfollow', views.unfollow_news_view, name='unfollow'),
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

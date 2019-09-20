from django.urls import path
from news import views


app_name = 'news'
urlpatterns = [
    path('', views.main_view, name='main'),
    path('create-news/', views.create_news_view, name='create'),
    path('detail:<int:news_id>/', views.news_detail_view, name='detail'),
    path('detail:<int:news_id>/unfollow', views.unfollow_news_view, name='unfollow'),
    path('detail:<int:news_id>/follow', views.follow_news_view, name='follow'),

    path('survey-detail:<int:survey_id>/', views.survey_detail_view, name='survey-detail'),
    path('create-survey/', views.survey_create_view, name='survey-create'),
    path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/yes', views.vote_yes_view, name='survey-yes'),
    path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/no', views.vote_no_view, name='survey-no'),
    path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/unvote', views.unvote_view, name='survey-unvote'),
    path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/modify', views.survey_option_modify_view, name='survey-option-modify'),
    path('survey-detail:<int:survey_id>/survey-option:<int:option_id>/delete', views.survey_option_delete_view, name='survey-option-delete'),
]

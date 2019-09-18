from django.urls import path
from news import views


app_name = 'news'
urlpatterns = [
    path('', views.main_view, name='main'),
    path('create/', views.create_news_view, name='create'),
    path('detail:<int:news_id>/', views.news_detail_view, name='detail'),
    path('detail:<int:news_id>/unfollow', views.unfollow_news_view, name='unfollow'),
    path('detail:<int:news_id>/follow', views.follow_news_view, name='follow'),

    path('survey_detail:<int:survey_id>/', views.survey_detail_view, name='survey-detail'),
    path('survey_detail:<int:survey_id>/survey_option:<int:option_id>/vote_yes', views.vote_yes_view, name='survey-yes'),
    path('survey_detail:<int:survey_id>/survey_option:<int:option_id>/vote_no', views.vote_no_view, name='survey-no'),
]

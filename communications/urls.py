from django.urls import path
from communications import views


app_name = 'communications'
urlpatterns = [
    path('threads:<str:thread_kind>/<str:tag_title>/', views.threads_view, name='threads'),
    path('thread/<int:thread_id>/<str:tag_title>/', views.thread_view, name='thread'),

    path('statement-create', views.statement_create_view, name='statement-create'),
    path('statements/<int:thread_id>/', views.statements, name='statements'),

    path('thread:<int:thread_id>/unfollow', views.unfollow_thread_view, name='unfollow'),
    path('thread:<int:thread_id>/follow', views.follow_thread_view, name='follow'),

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

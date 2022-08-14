from django.urls import path
from communications import views


app_name = 'communications'
urlpatterns = [
    # announcements
    # path('announcements:<str:tag_title>/', views.announcements_view, name='announcements'),
    path('threads:<str:thread_kind>/<str:tag_title>/', views.threads_view, name='threads'),
    
    path('thread:<int:thread_id>/<str:tag_title>/', views.thread_view, name='thread'),
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
    
    # path('', views.home, name='home'),
    # path('checkview', views.checkview, name='checkview'),
    # path('<str:room_name>/', views.room, name='room'),  # http://127.0.0.1:8000/communications/thread/THREAD_NAME/
    # path('send', views.send, name='send'),
    # path('getMessages/<str:room_name>/', views.getMessages, name='getMessages'),
    
    path('thread/<int:thread_id>/<str:tag_title>/', views.thread, name='thread'),
    path('send2', views.send2, name='send2'),
    path('getStatements/<int:thread_id>/', views.getStatements, name='getStatements'),
    
]

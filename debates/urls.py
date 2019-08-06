from django.urls import path
from debates import views


urlpatterns = [
    path('', views.debates_main_view, name='debates-main'),
    path('<int:topic_id>/<int:debate_id>/', views.debate_view, name='debate'),
    path('create_topic/', views.create_topic_view, name='create-topic'),
    path('topic:<int:topic_id>/create-debate/', views.create_debate_view, name='create-debate'),
    path('<int:topic_id>/<int:debate_id>/update-debate/', views.add_allowed_profiles_view, name='update-debate')
]

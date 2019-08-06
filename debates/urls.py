from django.urls import path
from debates import views


urlpatterns = [
    path('', views.debates_main_view, name='debates-main'),
    path('<slug:topic_slug>/<slug:debate_slug>/', views.debate_view, name='debate'),
    path('create_topic/', views.create_topic_view, name='create-topic'),
    path('<slug:topic_slug>/create_debate/', views.create_debate_view, name='create-debate'),
    path('<slug:topic_slug>/<slug:debate_slug>/update_debate/', views.add_allowed_profiles_view, name='update-debate')
]

from django.urls import path

from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    path('skills/<str:model_name>/', views.knowledge_packets_in_skills_view,
         name='knowledge-packets-in-skills'),
]

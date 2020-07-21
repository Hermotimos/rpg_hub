from django.urls import path

from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    path('skills/<str:skill_model>/', views.skills_view, name='skills'),
]

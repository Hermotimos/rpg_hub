from django.urls import path

from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    path('skills/<str:model_name>/', views.skills_view, name='skills'),
]

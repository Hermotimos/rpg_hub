from django.urls import path
from rules import views


app_name = 'rules'
urlpatterns = [
    path('', views.rules_main_view, name='main'),
    path('skills/', views.rules_skills_view, name='skills'),
    path('combat/', views.rules_combat_view, name='combat'),

]

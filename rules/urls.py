from django.urls import path
from rules import views


app_name = 'rules'
urlpatterns = [
    path('', views.rules_main_view, name='main'),
]

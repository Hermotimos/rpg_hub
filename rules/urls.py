from django.urls import path
from rules import views


urlpatterns = [
    path('', views.rules_main_view, name='rules-main'),

]

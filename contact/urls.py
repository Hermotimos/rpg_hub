from django.urls import path
from contact import views


urlpatterns = [
    path('', views.report_view, name='report'),
]

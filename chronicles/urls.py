from django.urls import path
from chronicles import views

app_name = 'chronicles'
urlpatterns = [
    path('', views.recreate, name='recreate'),
]

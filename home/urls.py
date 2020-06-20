from django.urls import path

from home import views


app_name = 'home'
urlpatterns = [
    path('', views.home_view, name='home'),
    # path('dupa/', views.dupa_view, name='dupa'),
    path('dupa/', views.DupaView.as_view(), name='dupa')
]

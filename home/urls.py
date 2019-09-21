from django.urls import path
from home import views


app_name = 'home'
urlpatterns = [
    path('', views.home_view, name='home'),
    path('dupa/', views.dupa_view, name='dupa'),
    path('reload-sorting-names/', views.reload_sorting_names_view, name='reload'),
]

from django.urls import path
from toponomikon import views


app_name = 'toponomikon'
urlpatterns = [
    path('', views.toponomikon_main_view, name='main'),
    path('<str:loc_name>/', views.toponomikon_location_view, name='location'),
]

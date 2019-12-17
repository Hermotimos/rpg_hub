from django.urls import path
from toponomikon import views


app_name = 'toponomikon'
urlpatterns = [
    path('', views.toponomikon_main_view, name='main'),
    path('gen_loc:<int:gen_loc_id>', views.toponomikon_general_location_view, name='general_location'),

]

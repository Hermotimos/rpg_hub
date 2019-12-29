from django.urls import path
from toponomikon import views


app_name = 'toponomikon'
urlpatterns = [
    path('', views.toponomikon_main_view, name='main'),
    path('gen-loc:<int:gen_loc_id>/', views.toponomikon_general_location_view, name='general-location'),
    path('spec-loc:<int:spec_loc_id>/', views.toponomikon_specific_location_view, name='specific-location'),
    path('gen-loc:<int:gen_loc_id>/spec-loc:<int:spec_loc_id>/inform/', views.toponomikon_inform_view, name='inform'),
]

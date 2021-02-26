from django.urls import path
from prosoponomikon import views


app_name = 'prosoponomikon'
urlpatterns = [
    path('_hidden', views.prosoponomikon_main_view, name='main'),
    path('ungrouped/', views.prosoponomikon_ungrouped_view, name='ungrouped'),
    path('grouped/', views.prosoponomikon_grouped_view, name='grouped'),
    path('groups-create/', views.prosoponomikon_character_group_create_view,
         name='groups-create'),
    path('groups-edit/<int:group_id>/',
         views.prosoponomikon_character_groups_edit_view,
         name='groups-edit'),
    path('character/<int:character_id>/', views.prosoponomikon_character_view,
         name='character'),
    
    path('character/<int:character_id>/bio-packet-form/<int:bio_packet_id>/',
         views.prosoponomikon_bio_packet_form_view,
         name='bio-packet-form'),
    
    path('names/', views.prosoponomikon_names_view, name='names'),

]

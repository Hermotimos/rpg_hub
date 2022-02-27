from django.urls import path
from prosoponomikon import views


app_name = 'prosoponomikon'
urlpatterns = [
    path('ungrouped/', views.prosoponomikon_ungrouped_view, name='ungrouped'),
    
    # path('grouped/', views.prosoponomikon_grouped_view, name='grouped'),
    # path('groups-create/', views.prosoponomikon_character_group_create_view,
    #      name='groups-create'),
    # path('groups-edit/', views.prosoponomikon_character_groups_edit_view,
    #      name='groups-edit'),
    
    path('character/<int:character_id>/', views.prosoponomikon_character_view,
         name='character'),
    path('character-for-gm/<int:character_id>/',
         views.prosoponomikon_character_for_gm_view,
         name='character-for-gm'),
    path('character-for-player/<int:character_id>/',
         views.prosoponomikon_character_for_player_view,
         name='character-for-player'),
    
    
    path('character/<int:character_id>/bio-packet-form/<int:bio_packet_id>/',
         views.prosoponomikon_bio_packet_form_view, name='bio-packet-form'),
    
    path('first-names/', views.prosoponomikon_first_names_view,
         name='first-names'),
    path('family-names/', views.prosoponomikon_family_names_view,
         name='family-names'),
    path('character-create/',  views.prosoponomikon_character_create_form_view,
         name='character-create'),
    
    path('acquaintances/<int:location_id>/',
         views.prosoponomikon_acquaintances_view,
         name='acquaintances'),

]

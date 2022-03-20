from django.urls import path
from prosoponomikon import views


app_name = 'prosoponomikon'
urlpatterns = [
    path('characters/', views.prosoponomikon_characters_view, name='characters'),
    path('character/<int:character_id>/', views.prosoponomikon_character_view,
         name='character'),
    path('character/<int:character_id>/bio-packet-form/<int:bio_packet_id>/',
         views.prosoponomikon_bio_packet_form_view, name='bio-packet-form'),
    
    path('first-names/', views.prosoponomikon_first_names_view, name='first-names'),
    path('family-names/', views.prosoponomikon_family_names_view, name='family-names'),
    
    path('character-create/',  views.prosoponomikon_character_create_form_view,
         name='character-create'),
    
    path('acquaintances/<int:location_id>/',
         views.prosoponomikon_acquaintances_view,
         name='acquaintances'),

]

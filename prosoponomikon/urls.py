from django.urls import path
from prosoponomikon import views


app_name = 'prosoponomikon'
urlpatterns = [
    path('', views.prosoponomikon_main_view, name='main'),
    path('ungrouped/', views.prosoponomikon_ungrouped_view, name='ungrouped'),
    path('grouped/', views.prosoponomikon_grouped_view, name='grouped'),
    path('groups-edit/<int:group_id>/', views.prosoponomikon_character_groups_edit_view,
         name='groups-edit'),
    path('character/<int:character_id>/', views.prosoponomikon_character_view,
         name='character'),
    path('character/<int:character_id>/bio_packet/<int:bio_packet_id>/',
         views.prosoponomikon_biography_packet_edit_view,
         name='biography-packet-edit'),
    # path('characters/', views.prosoponomikon_characters_view, name='characters'),

]

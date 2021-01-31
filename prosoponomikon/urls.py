from django.urls import path
from prosoponomikon import views


app_name = 'prosoponomikon'
urlpatterns = [
    path('', views.prosoponomikon_main_view, name='main'),
    path('character/<str:character_name>/', views.prosoponomikon_character_view,
         name='character'),
    path('ungrouped/', views.prosoponomikon_ungrouped_view, name='ungrouped'),
    path('grouped/', views.prosoponomikon_grouped_view, name='grouped'),
    path('groups-edit/<int:group_id>/', views.prosoponomikon_character_groups_edit_view,
         name='groups-edit'),
    # path('characters/', views.prosoponomikon_characters_view, name='characters'),

]

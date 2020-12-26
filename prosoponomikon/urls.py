from django.urls import path
from prosoponomikon import views


app_name = 'prosoponomikon'
urlpatterns = [
    path('', views.prosoponomikon_main_view, name='main'),
    path(
        'characters-ungrouped',
        views.prosoponomikon_characters_ungrouped_view,
        name='characters-ungrouped'
    ),
    path(
        'characters-grouped',
        views.prosoponomikon_characters_grouped_view,
        name='characters-grouped'
    ),
    path('prosopa/', views.prosoponomikon_prosopa_view, name='prosopa'),
    path('create-group/', views.prosoponomikon_character_group_create_view,
         name='create-group'),

]

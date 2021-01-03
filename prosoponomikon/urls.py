from django.urls import path
from prosoponomikon import views


app_name = 'prosoponomikon'
urlpatterns = [
    path('', views.prosoponomikon_main_view, name='main'),
    path(
        'personas-ungrouped',
        views.prosoponomikon_personas_ungrouped_view,
        name='personas-ungrouped'
    ),
    path(
        'personas-grouped',
        views.prosoponomikon_personas_grouped_view,
        name='personas-grouped'
    ),
    path('personas/', views.prosoponomikon_prosopa_view, name='personas'),
    path('create-group/', views.prosoponomikon_persona_group_create_view,
         name='create-group'),

]

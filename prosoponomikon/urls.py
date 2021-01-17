from django.urls import path
from prosoponomikon import views


app_name = 'prosoponomikon'
urlpatterns = [
    path('', views.prosoponomikon_main_view, name='main'),
    path('<str:persona_name>/', views.prosoponomikon_persona_view, name='persona'),
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
    path(
        'create-persona-group/',
        views.prosoponomikon_persona_group_create_view,
        name='create-persona-group',
    ),
    # path('personas/', views.prosoponomikon_personas_view, name='personas'),

]

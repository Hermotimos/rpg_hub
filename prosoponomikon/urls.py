from django.urls import path
from prosoponomikon import views


app_name = 'prosoponomikon'
urlpatterns = [
    path('', views.prosoponomikon_main_view, name='main'),
    path('character/<str:character_name>/', views.prosoponomikon_character_view,
         name='character'),
    path('ungrouped/', views.prosoponomikon_ungrouped_view, name='ungrouped'),
    path('grouped/', views.prosoponomikon_grouped_view, name='grouped'),
    path('create-group/', views.prosoponomikon_group_create_view,
         name='create-group'),
    # path('characters/', views.prosoponomikon_characters_view, name='characters'),

]

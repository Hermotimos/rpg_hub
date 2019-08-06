from django.urls import path
from debates import views


urlpatterns = [
    path('', views.debates_main_view, name='debates-main'),
    path('create_board/', views.create_board_view, name='create-board'),
    path('<slug:board_slug>/create_debate/', views.create_debate_view, name='create-debate'),
    path('<slug:board_slug>/<slug:debate_slug>/', views.debate_view, name='debate'),
    path('<slug:board_slug>/<slug:debate_slug>/update_debate/', views.add_allowed_profiles_view, name='update-debate')
]

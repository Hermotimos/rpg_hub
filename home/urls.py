from django.urls import path

from rpg_project.utils import query_debugger
from home import views


app_name = 'home'
urlpatterns = [
    path('', views.home_view, name='home'),
    # path('dupa/', views.dupa_view, name='dupa'),
    path('dupa/', query_debugger(views.DupaView.as_view()), name='dupa')
]

from django.urls import path

from knowledge import views
from rpg_project.utils import query_debugger


app_name = 'knowledge'
urlpatterns = [
    # FBV
    # path('almanac/', views.almanac_view, name='almanac'),
    # path('theology/', views.theology_view, name='theology'),
    
    # CBV
    path('almanac/', query_debugger(views.AlmanacView.as_view()),
         name='almanac'),
    path('theology/', query_debugger(views.TheologyView.as_view()),
         name='theology'),
]

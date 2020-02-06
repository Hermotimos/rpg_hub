from django.urls import path

from knowledge import views
from rpg_project.utils import query_debugger


app_name = 'knowledge'
urlpatterns = [
    # path('almanac/', views.knowledge_almanac_view, name='knowledge-almanac'),
    path('almanac/', query_debugger(views.AlmanacListView.as_view()), name='almanac'),
    # path('theology/', views.knowledge_theology_view, name='theology'),
    path('theology/', query_debugger(views.TheologyView.as_view()), name='theology'),
    path('inform:<int:kn_packet_id>/', views.knowledge_inform_view, name='inform')
]

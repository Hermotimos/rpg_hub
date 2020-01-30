from django.urls import path
from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    path('almanac/', views.knowledge_almanac_view, name='knowledge-almanac'),
    path('theology/', views.knowledge_theology_view, name='knowledge-theology'),
    path('inform:<int:kn_packet_id>/', views.knowledge_inform_view, name='knowledge-inform')
]

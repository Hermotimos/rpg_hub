from django.urls import path
from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    path('knowledge-sheet/', views.knowledge_sheet_view, name='knowledge-sheet'),
    path('knowledge-inform:<int:kn_packet_id>/', views.knowledge_inform_view, name='knowledge-inform')
]

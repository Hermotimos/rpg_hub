from django.urls import path

from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    path('kn-packets-in-skills/<str:model_name>/', views.knowledge_packets_in_skills_view,
         name='knowledge-packets-in-skills'),
    path('kn-packet/<int:kn_packet_id>/', views.knowledge_packet_view,
         name='knowledge-packet'),
]

from django.urls import path

from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    path('almanac/', views.almanac_view, name='almanac'),
    path('kn-packet-form/<int:kn_packet_id>/', views.kn_packet_form_view,  name='kn-packet-form'),
    path(
        'almanac/informables/<int:knowledge_packet_id>/',
        views.knowledge_packet_informables,
        name='kn-packet-informables'
    ),
]

from django.urls import path
from contact import views


app_name = 'contact'
urlpatterns = [
    path('', views.report_view, name='report'),
    path('reports-list/', views.reports_list_view, name='reports-list'),
    path('mark-done:<int:report_id>/', views.mark_done_view, name='done'),
    path('mark-undone:<int:report_id>/respond/', views.mark_done_and_respond_view, name='respond'),
    path('mark-undone:<int:report_id>/', views.mark_undone_view, name='undone'),

]

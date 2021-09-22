from django.urls import path
from technicalities import views


app_name = 'technicalities'
urlpatterns = [
    path('', views.reload_main_view, name='reload-main'),
    path('reload-chronicles/', views.reload_chronicles, name='reload-chronicles'),
    path('reload-imaginarion/', views.reload_imaginarion, name='reload-imaginarion'),
    path('reload-rules/', views.reload_rules, name='reload-rules'),
    path('reload-toponomikon/', views.reload_toponomikon, name='reload-toponomikon'),
    path('reload-prosoponomikon/', views.reload_prosoponomikon, name='reload-prosoponomikon'),
    # path('reload-packets/', views.reload_packets, name='reload-packets'),
    path('refresh-contenttypes/', views.refresh_content_types, name='refresh-contenttypes'),
    
    path('todos/', views.todos_view, name='todos'),
    path('backup-db/', views.backup_db_view, name='backup-db'),
    path('download-db/', views.download_db, name='download-db'),
]

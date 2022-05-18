from django.urls import path
from technicalities import views


app_name = 'technicalities'
urlpatterns = [
    path('', views.reload_main_view, name='reload-main'),
    path('todos/', views.todos_view, name='todos'),
    path('backup-db/', views.backup_db_view, name='backup-db'),
    path('update-local-db/', views.update_local_db_view, name='update-local-db'),
    path('allow-game-masters-to-all/', views.allow_game_masters_to_all, name='allow-game-masters-to-all'),
    path('refresh-contenttypes/', views.refresh_content_types, name='refresh-contenttypes'),
    path('cleanup-rules-objects/', views.cleanup_rules_objects, name='cleanup-rules-objects'),

    path('reload-chronicles/', views.reload_chronicles, name='reload-chronicles'),
    path('reload-imaginarion/', views.reload_imaginarion, name='reload-imaginarion'),
    path('reload-rules/', views.reload_rules, name='reload-rules'),
    path('reload-toponomikon/', views.reload_toponomikon, name='reload-toponomikon'),
    path('reload-prosoponomikon/', views.reload_prosoponomikon, name='reload-prosoponomikon'),
    
]

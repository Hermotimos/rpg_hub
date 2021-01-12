from django.urls import path
from reload import views


app_name = 'reload'
urlpatterns = [
    path('', views.reload_main_view, name='reload-main'),
    path('reload-history/', views.reload_history, name='reload-history'),
    path('reload-rules/', views.reload_rules, name='reload-rules'),
    path('reload-toponomikon/', views.reload_toponomikon, name='reload-toponomikon'),
    path('reload-prosoponomikon/', views.reload_prosoponomikon, name='reload-prosoponomikon'),
    path('refresh-contenttypes/', views.refresh_content_types, name='refresh-contenttypes'),
]

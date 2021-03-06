from django.urls import path
from reload import views


app_name = 'reload'
urlpatterns = [
    path('', views.reload_main_view, name='reload-main'),
    path('reload-chronicles/', views.reload_chronicles, name='reload-chronicles'),
    path('reload-imaginarion/', views.reload_imaginarion, name='reload-imaginarion'),
    path('reload-rules/', views.reload_rules, name='reload-rules'),
    path('reload-toponomikon/', views.reload_toponomikon, name='reload-toponomikon'),
    path('reload-prosoponomikon/', views.reload_prosoponomikon, name='reload-prosoponomikon'),
    path('refresh-contenttypes/', views.refresh_content_types, name='refresh-contenttypes'),
]

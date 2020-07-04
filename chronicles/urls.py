from django.urls import path
from chronicles import views_recreate
from chronicles import views

app_name = 'chronicles'
urlpatterns = [
    path('', views_recreate.recreate, name='recreate'),
    
    path('chapters', views.chapters_view, name='chapters'),

]

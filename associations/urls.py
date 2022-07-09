from django.urls import path
from associations import views

app_name = 'associations'
urlpatterns = [
    path('comments/', views.comments_view, name='comments'),
    # path('associations/', views.associations_view, name='associations'),
]
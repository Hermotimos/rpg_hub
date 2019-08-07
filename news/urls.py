from django.urls import path
from news import views


app_name = 'news'
urlpatterns = [
    path('', views.news_view, name='main'),
    path('create/', views.create_news_view, name='create'),
    path('detail:<slug:news_slug>/', views.news_detail_view, name='detail')
]

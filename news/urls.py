from django.urls import path
from news import views


urlpatterns = [
    path('', views.news_view, name='news-list'),
    path('news-create/', views.create_news_view, name='news-create'),
    path('<slug:news_slug>/', views.news_detail_view, name='news-detail')
]

from django.urls import path
from .views import news_view, create_news_view

urlpatterns = [
    path('', news_view, name='news-main'),
    path('news-create/', create_news_view, name='news-create')
]
from django.urls import path
from .views import news_view, create_news_view, news_detail_view


urlpatterns = [
    path('', news_view, name='news-list'),
    path('news-create/', create_news_view, name='news-create'),
    path('<slug:slug>/', news_detail_view, name='news-detail')
]

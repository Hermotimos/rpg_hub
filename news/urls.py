from django.urls import path
from .views import news_view, create_news_view, news_detail_vew

urlpatterns = [
    path('', news_view, name='news-main'),
    path('news-create/', create_news_view, name='news-create'),
    path('news-detail/', news_detail_vew, name='news-detail')
]

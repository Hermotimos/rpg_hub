from django.urls import path
from .views import register, LoginView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(), name='login')
]

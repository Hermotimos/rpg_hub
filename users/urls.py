from django.urls import path
from users.views import register_view, profile_view, change_password_view, LoginView, LogoutView

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('change_password/', change_password_view, name='change_password')
]

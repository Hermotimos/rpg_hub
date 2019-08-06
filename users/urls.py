from django.urls import path
from users import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/change_password/', views.change_password_view, name='change-password')
]

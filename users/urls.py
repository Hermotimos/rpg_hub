from django.urls import path
from users import views


app_name = 'users'
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('change_password/', views.change_password_view, name='change-password'),
    path('profile/', views.profile_view, name='profile'),
    path('switch-profile:<int:profile_id>/', views.switch_profile, name='switch-profile'),
]

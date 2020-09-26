from django.urls import path
from development import views


app_name = 'development'
urlpatterns = [
    path('profile-sheet:<int:profile_id>/', views.profile_sheet_view,
         name='profile-sheet'),
]

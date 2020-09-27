from django.urls import path
from development import views


app_name = 'development'
urlpatterns = [
    path('profile-sheet:<int:profile_id>/', views.profile_sheet_view,
         name='profile-sheet'),
    
    path('character-skills:<int:profile_id>/', views.character_skills_view,
         name='skills'),
    path('character-skills-for-gm/', views.character_skills_for_gm_view,
         name='skills-for-gm'),

]

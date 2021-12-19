from django.urls import path
from development import views


app_name = 'development'
urlpatterns = [
    
    path('character-skills:<int:profile_id>/', views.character_skills_view,
         name='skills'),
    path('character-skills-for-gm/', views.character_skills_for_gm_view,
         name='skills-for-gm'),
    path('character-tricks/', views.character_tricks_view, name='tricks'),

]

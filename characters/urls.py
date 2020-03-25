from django.urls import path

from characters import views
from rpg_project.utils import query_debugger

# app_name = 'characters'
# urlpatterns = [
    # CBV
    # path('tricks/', query_debugger(views.CharacterTricksView.as_view()), name='tricks'),
    # path('character-skills:<int:profile_id>/', query_debugger(views.CharacterSkillsView.as_view()),
    #      name='character-skills'),
    # path('character-all-skills-for-gm/', query_debugger(views.CharacterAllSkillsForGmView.as_view()),
    #      name='character-all-skills-for-gm'),
    # FBV
    # path('tricks/', views.character_tricks_view, name='tricks'),
    # path('character-skills:<int:profile_id>/', views.character_skills_view, name='character-skills'),
    # path('character-all-skills-for-gm/', views.skills_sheets_for_gm_view, name='character-all-skills-for-gm'),
# ]

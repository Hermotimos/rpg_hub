from django.urls import path

from characters import views
from rpg_project.utils import query_debugger

app_name = 'characters'
urlpatterns = [
    # path('tricks/', views.tricks_view, name='tricks'),
    path('tricks/', query_debugger(views.CharacterTricksView.as_view()), name='tricks'),
    # path('character-skills:<int:profile_id>/', views.skills_sheet_view, name='character-skills'),
    path('character-skills:<int:profile_id>/', query_debugger(views.CharacterSkillsView.as_view()), name='character-skills'),
    # path('skills-sheets-for-gm/', views.skills_sheets_for_gm_view, name='skills-sheets-for-gm'),
    path('skills-sheets-for-gm/', query_debugger(views.SkillsForGmView.as_view()), name='skills-sheets-for-gm'),

]

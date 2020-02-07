from django.urls import path

from characters import views
from rpg_project.utils import query_debugger

app_name = 'characters'
urlpatterns = [
    # path('tricks/', views.tricks_view, name='tricks'),
    path('tricks/', query_debugger(views.TricksView.as_view()), name='tricks'),
    path('skills-sheet:<int:profile_id>/', views.skills_sheet_view, name='skills-sheet'),
    # path('skills-sheets-for-gm/', views.skills_sheets_for_gm_view, name='skills-sheets-for-gm'),
    path('skills-sheets-for-gm/', query_debugger(views.SkillsForGmView.as_view()), name='skills-sheets-for-gm'),

]

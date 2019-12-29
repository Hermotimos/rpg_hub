from django.urls import path
from characters import views


app_name = 'characters'
urlpatterns = [
    path('tricks-sheet/', views.tricks_sheet_view, name='tricks-sheet'),
    path('skills-sheet:<int:profile_id>/', views.skills_sheet_view, name='skills-sheet'),
    path('skills-sheets-for-gm/', views.skills_sheets_for_gm_view, name='skills-sheets-for-gm'),

]

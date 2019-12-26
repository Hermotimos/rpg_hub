from django.urls import path
from characters import views


app_name = 'characters'
urlpatterns = [
    path('tricks-sheet/', views.tricks_sheet_view, name='tricks-sheet'),
    path('character-skills/', views.character_skills_view, name='character-skills'),
    path('character-knowledge-packets/', views.character_knowledge_packets_view, name='knowledge-packets-skills')

]

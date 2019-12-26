from django.urls import path
from characters import views


app_name = 'characters'
urlpatterns = [
    path('tricks-sheet/', views.tricks_sheet_view, name='tricks-sheet'),
    path('character-skills/', views.skills_sheet_view, name='skills-sheet'),
]

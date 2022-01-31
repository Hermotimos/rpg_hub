from django.urls import path
from rules import views


app_name = 'rules'
urlpatterns = [
    path('', views.rules_main_view, name='main'),
    path('armor/', views.rules_armor_view, name='armor'),
    path('character-sheet/', views.rules_character_sheet_view, name='character-sheet'),
    path('combat/', views.rules_combat_view, name='combat'),
    path('masteries/', views.rules_masteries_view, name='masteries'),
    path('professions/', views.rules_professions_view, name='professions'),
    path('skills-and-synergies/', views.rules_skills_view, name='skills-and-synergies'),
    path('skills-list/', views.rules_skills_list_view, name='skills-list'),
    path('synergies-list/', views.rules_synergies_list_view, name='synergies-list'),
    path('tests/', views.rules_tests_view, name='tests'),
    path('traits/', views.rules_traits_view, name='traits'),
    path('tricks/', views.rules_tricks_view, name='tricks'),
    path('weapons/', views.rules_weapons_view, name='weapons'),
    path('wounds/', views.rules_wounds_view, name='wounds'),
    # path('combat/pdf/', html2pdf_views.yet_another, name='combat-pdf'),
    # path('combat/pdf2/', html2pdf_views.export_word_2, name='combat-pdf2'),

]

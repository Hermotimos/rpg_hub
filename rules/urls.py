from django.urls import path
from rules import views


app_name = 'rules'
urlpatterns = [
    path('', views.rules_main_view, name='main'),
    path('armor/', views.rules_armor_view, name='armor'),
    path('character-sheet/', views.rules_character_sheet_view, name='character-sheet'),
    path('combat/', views.rules_combat_view, name='combat'),
    path('experience-demand/', views.rules_experience_demand_view, name='experience-demand'),
    path('fitness-and-tricks/', views.rules_fitness_and_tricks_view, name='fitness-and-tricks'),
    path('professions/', views.rules_professions_view, name='professions'),
    path('skills-and-synergies/', views.rules_skills_view, name='skills-and-synergies'),
    path('skills-list/<str:skilltype_kind>/', views.rules_skills_list_view, name='skills-list'),
    path('synergies-list/', views.rules_synergies_list_view, name='synergies-list'),
    path('tests/', views.rules_tests_view, name='tests'),
    path('traits/', views.rules_traits_view, name='traits'),
    path('power-trait/', views.rules_power_trait_view, name='power-trait'),
    path('power-priests/', views.rules_power_priests_view, name='power-priests'),
    path('power-sorcerers/', views.rules_power_sorcerers_view, name='power-sorcerers'),
    path('power-theurgists/', views.rules_power_theurgists_view, name='power-theurgists'),
    path('weapons/', views.rules_weapons_view, name='weapons'),
    path('wounds/', views.rules_wounds_view, name='wounds'),
]

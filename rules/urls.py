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
    
    path('character/', views.rules_character_view, name='character'),
    path('professions/<str:profession_type>/', views.rules_professions_view, name='professions'),
    
    path('character-development/', views.rules_character_development_view, name='character-development'),
    path('skills/<str:skilltype_kind>/', views.rules_skills_view, name='skills'),
    path('synergies/<str:skilltype_kind>/', views.rules_synergies_view, name='synergies'),
    
    path('tests/', views.rules_tests_view, name='tests'),
    path('traits/', views.rules_traits_view, name='traits'),
    path('power-trait/', views.rules_power_trait_view, name='power-trait'),
    path('priesthood/', views.rules_priesthood_view, name='priesthood'),
    path('sorcery/', views.rules_sorcery_view, name='sorcery'),
    path('theurgy/', views.rules_theurgy_view, name='theurgy'),
    path('weapon-types/', views.rules_weapon_types_view, name='weapon-types'),
    path('wounds/', views.rules_wounds_view, name='wounds'),
]

from django.urls import path
from rules import views


app_name = 'rules'
urlpatterns = [
    path('', views.rules_main_view, name='main'),
    path('skills/', views.rules_skills_view, name='skills'),
    path('combat/', views.rules_combat_view, name='combat'),
    path('traits/', views.rules_traits_view, name='traits'),
    path('professions/', views.rules_professions_view, name='professions'),
    # path('combat/pdf/', html2pdf_views.yet_another, name='combat-pdf'),
    # path('combat/pdf2/', html2pdf_views.export_word_2, name='combat-pdf2'),

]

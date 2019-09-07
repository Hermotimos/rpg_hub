from django.urls import path
from rules import views

from rules.html2pdf_views import generate_pdf_view

app_name = 'rules'
urlpatterns = [
    path('', views.rules_main_view, name='main'),
    path('skills/', views.rules_skills_view, name='skills'),
    path('combat/', views.rules_combat_view, name='combat'),

    path('combat/pdf/', generate_pdf_view, name='combat-pdf')
]

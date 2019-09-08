from django.urls import path
from rules import views
from rules import html2pdf_views


app_name = 'rules'
urlpatterns = [
    path('', views.rules_main_view, name='main'),
    path('skills/', views.rules_skills_view, name='skills'),
    path('combat/', views.rules_combat_view, name='combat'),

    path('combat/pdf/', html2pdf_views.generate_pdf_view, name='combat-pdf'),
    path('combat/pdf2/', html2pdf_views.generate_pdf_view_2, name='combat-pdf2'),

]

from django.urls import path
from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    path('knowledge-sheet/', views.knowledge_sheet, name='knowledge-sheet')

]

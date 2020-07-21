from django.urls import path

from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    path('skills/<str:skill_model>/', views.skills_view, name='skills'),
    
    # path('almanac/', views.almanac_view, name='almanac'),
    # path('books/', views.books_view, name='books'),
    # path('theology/', views.theology_view, name='theology'),
]

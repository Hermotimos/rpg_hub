from django.urls import path
from contact import views


app_name = 'contact'
urlpatterns = [
    path('', views.demand_view, name='demand'),
    path('demands-list/', views.demands_list_view, name='demands-list'),
    path('mark-done:<int:demand_id>/', views.mark_done_view, name='done'),
    path('mark-done:<int:demand_id>/done-answer/', views.mark_done_and_answer_view, name='done-answer'),
    path('mark-undone:<int:demand_id>/', views.mark_undone_view, name='undone'),

]

from django.urls import path
from contact import views


app_name = 'contact'
urlpatterns = [
    path('demands/', views.main_view, name='main'),
    path('demands/todo', views.todo_view, name='todo'),
    path('demands/create', views.create_demand_view, name='create'),
    path('demands/delete:<int:demand_id>/', views.delete_demand_view, name='delete'),
    path('demands/modify:<int:demand_id>/', views.modify_demand_view, name='modify'),
    path('demands/detail:<int:demand_id>/', views.demand_detail_view, name='detail'),
    path('demands/mark-done:<int:demand_id>/', views.mark_done_view, name='done'),
    path('demands/mark-done:<int:demand_id>/answer/', views.mark_done_and_answer_view, name='done-answer'),
    path('demands/mark-undone:<int:demand_id>/', views.mark_undone_view, name='undone'),

]

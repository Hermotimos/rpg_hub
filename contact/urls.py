from django.urls import path
from contact import views


app_name = 'contact'
urlpatterns = [
    path('demands/', views.demands_view, name='main'),
    path('demands/create', views.create_demand_view, name='create'),
    path('demands/delete:<int:demand_id>/', views.delete_demand_view, name='delete'),
    path('demands/modify:<int:demand_id>/', views.modify_demand_view, name='modify-demand'),

    path('demands/todo', views.todo_view, name='todo'),
    path('demands/create-todo', views.create_todo_view, name='create-todo'),
    path('demands/todo/modify:<int:demand_id>/', views.modify_todo_view, name='modify-todo'),

    path('demands/detail:<int:demand_id>/', views.demand_detail_view, name='detail'),
    path('demands/mark-done:<int:demand_id>/', views.mark_done_view, name='done'),
    path('demands/mark-undone:<int:demand_id>/', views.mark_undone_view, name='undone'),

]

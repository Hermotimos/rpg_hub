from django.urls import path
from contact import views


app_name = 'contact'
urlpatterns = [
    # demands
    path('demands/main/', views.demands_main_view, name='demands-main'),
    path('demands/create/', views.demands_create_view, name='demands-create'),
    path('demands/delete:<int:demand_id>/', views.demands_delete_view,
         name='demands-delete'),
    path('demands/detail:<int:demand_id>/', views.demands_detail_view,
         name='demands-detail'),
    path('demands/mark-done:<int:demand_id>/', views.mark_done_view,
         name='done'),
    path('demands/mark-undone:<int:demand_id>/', views.mark_undone_view,
         name='undone'),
    
    # plans
    path('plans/main/', views.plans_main_view, name='plans-main'),
    path('plans/for-gm/', views.plans_for_gm_view, name='plans-for-gm'),
    path('plans/create/', views.plans_create_view, name='plans-create'),
    path('plans/delete:<int:plan_id>/', views.plans_delete_view,
         name='plans-delete'),
    path('plans/modify:<int:plan_id>/', views.plans_modify_view,
         name='plans-modify'),
]

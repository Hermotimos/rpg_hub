from django.urls import include, path

from contact import views


app_name = 'contact'
urlpatterns = [

    path(
        'demands/',
        include(
            [
                path('main/', views.demands_main_view, name='demands-main'),
                path('create/', views.demands_create_view, name='demands-create'),
                path('delete:<int:demand_id>/', views.demands_delete_view, name='demands-delete'),
                path('detail:<int:demand_id>/', views.demands_detail_view, name='demands-detail'),
                path('done-undone:<int:demand_id>/done',
                    views.demand_done_undone_view, {'is_done': True},
                    name='demand-done'),
                path('done-undone:<int:demand_id>/undone',
                    views.demand_done_undone_view, {'is_done': False},
                    name='demand-undoned'),
            ]
        )

     ),

    path(
        'plans/',
        include(
            [
                path('main/', views.plans_main_view, name='plans-main'),
                path('for-gm/', views.plans_for_gm_view, name='plans-for-gm'),
                path('create/', views.plans_create_view, name='plans-create'),
                path('delete:<int:plan_id>/', views.plans_delete_view, name='plans-delete'),
                path('modify:<int:plan_id>/', views.plans_modify_view, name='plans-modify'),
            ]
        )
    ),
]

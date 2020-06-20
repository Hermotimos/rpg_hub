from django.urls import path

from knowledge import views


app_name = 'knowledge'
urlpatterns = [
    # FBV
    # path('almanac/', views.almanac_view, name='almanac'),
    # path('theology/', views.theology_view, name='theology'),
    
    # CBV
    path('almanac/', views.AlmanacView.as_view(), name='almanac'),
    path('theology/', views.TheologyView.as_view(), name='theology'),
]

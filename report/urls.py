from django.urls import path
from report.views import report_view


urlpatterns = [
    path('', report_view, name='report'),
]

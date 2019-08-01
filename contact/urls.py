from django.urls import path
from contact.views import report_view


urlpatterns = [
    path('', report_view, name='report'),
]

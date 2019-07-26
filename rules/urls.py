from django.urls import path
from rules.views import rules_main_view


urlpatterns = [
    path('', rules_main_view, name='rules_main'),

]

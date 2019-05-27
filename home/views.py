from django.shortcuts import render


def home_view(request):
    render(request, 'home.html', {})

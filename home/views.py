from django.shortcuts import render, redirect


def home_view(request):
    context = {
        'page_title': 'Home'
    }
    return redirect('login')

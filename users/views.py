from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            messages.success(request, f'Utworzono konto dla {username}!')
            return redirect('home')
    else:
        form = UserCreationForm

    context = {
        'page_title': 'Rejestracja',
        'form': form
    }
    return render(request, 'users/register.html', context)

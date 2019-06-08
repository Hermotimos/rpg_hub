from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST or None)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Utworzono konto dla {username}!')
            return redirect('home')
    else:
        form = UserRegistrationForm

    context = {
        'page_title': 'Rejestracja',
        'form': form
    }
    return render(request, 'users/register.html', context)

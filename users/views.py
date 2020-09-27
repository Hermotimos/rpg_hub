from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView

from django.shortcuts import render, redirect

from rules.models import Skill, SkillLevel, Synergy, SynergyLevel
from users.forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from users.models import Profile


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST or None)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.info(request, f'Utworzono konto dla {username}! Zaloguj się!')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()

    context = {
        'page_title': 'Utwórz profil',
        'form': form
    }
    return render(request, 'users/register.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.info(request, 'Zaktualizowano profil postaci!')
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'page_title': 'Profil',
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/profile.html', context)


@login_required()
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.info(request, 'Hasło zostało zaktualizowane!')
            return redirect('users:profile')
        else:
            messages.warning(request, 'Popraw poniższy błąd!')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'page_title': 'Zmiana hasła',
        'form': form
    }
    return render(request, 'users/change_password.html', context)


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Logowanie'
        return context
        
        
class CustomLogoutView(LogoutView):
    template_name = 'users/logout.html'


from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import F, Max
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from prosoponomikon.forms import CharacterForm
from prosoponomikon.models import Character
from users.forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from users.models import Profile
from prosoponomikon.models import FirstName

from django.contrib.auth import login


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    # settings.py
    # LOGIN_REDIRECT_URL = 'home:home'
    # LOGIN_URL = 'users:login'
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        # Determine user's default profile to present opon logon
        try:
            profile = user.profiles.get(status='gm')
        except (Profile.DoesNotExist, Profile.MultipleObjectsReturned):
            try:
                profile = user.profiles.get(status='player', is_alive=True)
            except (Profile.DoesNotExist, Profile.MultipleObjectsReturned):
                profile = user.profiles.annotate(
                    latest_gameevent_id=Max('events_known_directly__id')
                ).latest('latest_gameevent_id')
        self.request.session['profile_id'] = profile.id
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Logowanie'
        return context


class CustomLogoutView(LogoutView):
    # settings.py
    # LOGOUT_REDIRECT_URL = 'users:login'
    pass


def register_view(request):
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        profile = Profile.objects.create(user=user)
        Character.objects.create(
            profile=profile,
            first_name=FirstName.objects.create(
                form=user.username.replace('_', ' '))
        )
        messages.info(
            request, f'Utworzono konto dla {user.username}! Zaloguj się!')
        return redirect('users:login')

    context = {
        'page_title': 'Utwórz profil',
        'form': form
    }
    return render(request, 'users/register.html', context)


@login_required()
def change_password_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])

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
        'current_profile': profile,
        'page_title': 'Zmiana hasła',
        'form': form
    }
    return render(request, 'users/change_password.html', context)


@login_required
def profile_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=profile)
        character_form = CharacterForm(
            request.POST, instance=profile.character)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            character_form.save()
            messages.info(request, 'Zaktualizowano profil postaci!')
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
        character_form = CharacterForm(instance=profile.character)

    context = {
        'current_profile': profile,
        'page_title': 'Profil',
        'user_form': user_form,
        'profile_form': profile_form,
        'character_form': character_form,
    }
    return render(request, 'users/profile.html', context)


@login_required()
def switch_profile(request, profile_id):
    request.session['profile_id'] = profile_id
    chosen_profile = Profile.objects.get(id=profile_id)
    
    msg = f"Zmieniono Postać na {chosen_profile.character_name_copy}!"
    messages.info(request, msg)
    
    response = redirect(request.META.get('HTTP_REFERER'))
    if '/dupa/' in response['Location']:
        msg = """
            Przekierowano do strony startowej!
            (Wybrana Postać nie ma dostępu do poprzedniej treści)"""
        messages.warning(request, msg)
        return redirect('home:home')

    return response
    

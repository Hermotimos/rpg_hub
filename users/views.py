from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.db.models.functions import Length
from django.shortcuts import redirect
from django.shortcuts import render

from prosoponomikon.forms import CharacterForm
from prosoponomikon.models import Character, FirstName
from rpg_project.utils import sample_from_qs
from users.forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, UserImageUpdateForm
from users.models import Profile


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    # settings.py
    # LOGIN_REDIRECT_URL = 'users:home'
    # LOGIN_URL = 'users:login'
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        self.request.session['profile_id'] = get_profile(user).id
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
    current_profile = Profile.objects.get(id=request.session['profile_id'])

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.info(request, 'Hasło zostało zaktualizowane!')
            return redirect('users:edit-profile')
        else:
            messages.warning(request, 'Popraw poniższy błąd!')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'current_profile': current_profile,
        'page_title': 'Zmiana hasła',
        'form': form
    }
    return render(request, 'users/change_password.html', context)


@login_required
def edit_user_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        user_image_form = UserImageUpdateForm(request.POST, request.FILES)
        
        if user_form.is_valid() and user_image_form.is_valid():
            user_form.save()
            user_image = user_image_form.cleaned_data.get('user_image')
            if user_image:
                for profile in user_profiles:
                    profile.user_image = user_image
                    profile.save()

            messages.info(request, 'Zaktualizowano Użytkownika!')
            return redirect('users:edit-user')
    else:
        user_form = UserUpdateForm(instance=request.user)
        user_image_form = UserImageUpdateForm()

    context = {
        'current_profile': current_profile,
        'page_title': 'Konto Użytkownika',
        'user_form': user_form,
        'user_image_form': user_image_form,
    }
    return render(request, 'users/edit_user.html', context)


@login_required
def edit_profile_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=current_profile)
        character_form = CharacterForm(request.POST, instance=current_profile.character)
        if profile_form.is_valid() and character_form.is_valid():
            profile_form.save()
            character_form.save()
            messages.info(request, 'Zaktualizowano Postać!')
            return redirect('users:edit-profile')
    else:
        profile_form = ProfileUpdateForm(instance=current_profile)
        character_form = CharacterForm(instance=current_profile.character)

    context = {
        'current_profile': current_profile,
        'page_title': 'Edycja Postaci',
        'profile_form': profile_form,
        'character_form': character_form,
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
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
        return redirect('users:home')

    return response


# =============================================================================


def get_profile(user):
    """Get User's Profile by the priority of 'status' and probable recent use."""
    profiles = user.profiles.order_by('status', '-is_alive', '-is_active', 'character_name_copy')
    return profiles.first()


@login_required
def home_view(request):
    try:
        current_profile = Profile.objects.get(id=request.session['profile_id'])
    except KeyError:
        current_profile = get_profile(request.user)
        request.session['profile_id'] = current_profile.id
    
    known_characters = current_profile.characters_known_annotated()
    known_locations = current_profile.locations_known_annotated()
    known_gameevents = current_profile.gameevents_known_annotated().annotate(
        text_len=Length('description_long')).filter(text_len__gt=5)
    
    # set() ensures that if len(known) < k, than duplicates will be removed
    rand_characters = sample_from_qs(qs=known_characters, max_size=4)
    rand_locations = sample_from_qs(qs=known_locations, max_size=2)
    rand_gameevents = sample_from_qs(qs=known_gameevents, max_size=1)
    print(rand_gameevents)
    context = {
        'current_profile': current_profile,
        'page_title': 'Hyllemath',
        'rand_characters': rand_characters,
        'rand_locations': rand_locations,
        'rand_gameevents': rand_gameevents,
    }
    return render(request, 'users/home.html', context)


@login_required
def dupa_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Dupa',
    }
    return render(request, 'users/dupa.html', context)

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import get_current_site
from django.db.models import Prefetch, Q
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

    
#
# # (added page_title to context, changed template_name = 'users/login.html')
# class LoginView(SuccessURLAllowedHostsMixin, FormView):
#     """
#     Display the login form and handle the login action.
#     """
#     form_class = AuthenticationForm
#     authentication_form = None
#     redirect_field_name = REDIRECT_FIELD_NAME
#     template_name = 'users/login.html'
#     redirect_authenticated_user = True
#     extra_context = None
#
#     @method_decorator(sensitive_post_parameters())
#     @method_decorator(csrf_protect)
#     @method_decorator(never_cache)
#     def dispatch(self, request, *args, **kwargs):
#         if self.redirect_authenticated_user and self.request.user.is_authenticated:
#             redirect_to = self.get_success_url()
#             if redirect_to == self.request.path:
#                 raise ValueError(
#                     "Redirection loop for authenticated user detected. Check that "
#                     "your LOGIN_REDIRECT_URL doesn't point to a login page."
#                 )
#             return HttpResponseRedirect(redirect_to)
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_success_url(self):
#         url = self.get_redirect_url()
#         return url or resolve_url(settings.LOGIN_REDIRECT_URL)
#
#     def get_redirect_url(self):
#         """Return the user-originating redirect URL if it's safe."""
#         redirect_to = self.request.POST.get(
#             self.redirect_field_name,
#             self.request.GET.get(self.redirect_field_name, '')
#         )
#         url_is_safe = url_has_allowed_host_and_scheme(
#             url=redirect_to,
#             allowed_hosts=self.get_success_url_allowed_hosts(),
#             require_https=self.request.is_secure(),
#         )
#         return redirect_to if url_is_safe else ''
#
#     def get_form_class(self):
#         return self.authentication_form or self.form_class
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['request'] = self.request
#         return kwargs
#
#     def form_valid(self, form):
#         """Security check complete. Log the user in."""
#         auth_login(self.request, form.get_user())
#         return HttpResponseRedirect(self.get_success_url())
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         current_site = get_current_site(self.request)
#         context.update({
#             self.redirect_field_name: self.get_redirect_url(),
#             'site': current_site,
#             'site_name': current_site.name,
#             **(self.extra_context or {}),
#             'page_title': 'Logowanie',
#         })
#         return context
#
#
# class LogoutView(SuccessURLAllowedHostsMixin, TemplateView):
#     """
#     Log out the user and display the 'You are logged out' message.
#     """
#     next_page = None
#     redirect_field_name = REDIRECT_FIELD_NAME
#     template_name = 'users/logout.html'
#     extra_context = None
#
#     @method_decorator(never_cache)
#     def dispatch(self, request, *args, **kwargs):
#         auth_logout(request)
#         next_page = self.get_next_page()
#         if next_page:
#             # Redirect to this page until the session has been cleared.
#             return HttpResponseRedirect(next_page)
#         return super().dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         """Logout may be done via POST."""
#         return self.get(request, *args, **kwargs)
#
#     def get_next_page(self):
#         if self.next_page is not None:
#             next_page = resolve_url(self.next_page)
#         elif settings.LOGOUT_REDIRECT_URL:
#             next_page = resolve_url(settings.LOGOUT_REDIRECT_URL)
#         else:
#             next_page = self.next_page
#
#         if (self.redirect_field_name in self.request.POST or
#                 self.redirect_field_name in self.request.GET):
#             next_page = self.request.POST.get(
#                 self.redirect_field_name,
#                 self.request.GET.get(self.redirect_field_name)
#             )
#             url_is_safe = url_has_allowed_host_and_scheme(
#                 url=next_page,
#                 allowed_hosts=self.get_success_url_allowed_hosts(),
#                 require_https=self.request.is_secure(),
#             )
#             # Security check -- Ensure the user-originating redirection URL is safe.
#             if not url_is_safe:
#                 next_page = self.request.path
#         return next_page
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         current_site = get_current_site(self.request)
#         context.update({
#             'site': current_site,
#             'site_name': current_site.name,
#             'topic_name': 'Logged out',
#             **(self.extra_context or {}),
#             'page_title': 'Wylogowanie'
#         })
#         return context


# CHARACTER VIEWS


@login_required
def character_tricks_view(request):
    profile = request.user.profile
    
    if profile.status == 'gm':
        players_profiles = Profile.objects.exclude(
            Q(status='dead_player') | Q(status='living_npc')
            | Q(status='dead_npc') | Q(status='gm')
        )
    else:
        players_profiles = [profile]

    context = {
        'page_title': f'Podstępy - {profile.character_name}',
        'players_profiles': players_profiles
    }
    return render(request, 'users/character_tricks.html', context)



@login_required
def character_skills_view(request, profile_id='0'):
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        profile = request.user.profile

    skills = Skill.objects\
        .filter(skill_levels__acquired_by=profile)\
        .exclude(name__icontains='Doktryn')\
        .prefetch_related(Prefetch(
            'skill_levels',
            queryset=SkillLevel.objects.filter(acquired_by=profile)
        ))\
        .distinct()

    synergies = Synergy.objects\
        .filter(synergy_levels__acquired_by=profile) \
        .prefetch_related(Prefetch(
            'synergy_levels',
            queryset=SynergyLevel.objects.filter(acquired_by=profile)
        )) \
        .distinct()

    context = {
        'page_title': f'Umiejętności - {profile.character_name}',
        'skills': skills,
        'synergies': synergies,
    }
    if request.user.profile.status != 'gm' and profile_id != 0:
        return redirect('home:dupa')
    else:
        return render(request, 'users/character_skills.html', context)



@login_required
def character_skills_for_gm_view(request):
    profile = request.user.profile
    profiles = Profile.objects.filter(
        status__in=['active_player', 'inactive_player', 'dead_player']
    )
    
    context = {
        'page_title': 'Umiejętności graczy',
        'profiles': profiles,
    }
    if profile.status == 'gm':
        return render(request, 'users/character_all_skills_for_gm.html', context)
    else:
        return redirect('home:dupa')

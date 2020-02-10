from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from characters.models import Character
from rules.models import Skill, SkillLevel, Synergy, SynergyLevel
from users.models import Profile


class CharacterTricksView(View):

    @method_decorator(login_required)
    def get(self, request):
        profile = request.user.profile

        if profile.character_status == 'gm':
            players_profiles = Profile.objects.exclude(Q(character_status='dead_player') |
                                                       Q(character_status='living_npc') |
                                                       Q(character_status='dead_npc') |
                                                       Q(character_status='gm'))
        else:
            players_profiles = [profile]

        context = {
            'page_title': f'Podstępy - {profile.character_name}',
            'players_profiles': players_profiles
        }
        return render(request, 'characters/character_tricks.html', context)


class CharacterSkillsView(View):

    @method_decorator(login_required)
    def get(self, request, profile_id='0'):
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            profile = request.user.profile

        skills = Skill.objects \
            .filter(skill_levels__acquired_by_characters=profile.character) \
            .exclude(name__icontains='Doktryn') \
            .prefetch_related(Prefetch(
                'skill_levels',
                queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)
            )) \
            .distinct()

        synergies = Synergy.objects \
            .filter(synergy_levels__acquired_by_characters=profile.character) \
            .prefetch_related(Prefetch(
                'synergy_levels',
                queryset=SynergyLevel.objects.filter(acquired_by_characters=profile.character)
            )) \
            .distinct()

        context = {
            'page_title': f'Umiejętności - {profile.character_name}',
            'skills': skills,
            'synergies': synergies,
        }
        if request.user.profile.character_status != 'gm' and profile_id != 0:
            return redirect('home:dupa')
        else:
            return render(request, 'characters/skills_sheet.html', context)


class SkillsForGmView(View):

    @method_decorator(login_required)
    def get(self, request):
        profile = request.user.profile
        characters = Character.objects.all().select_related('profile')

        context = {
            'page_title': 'Umiejętności graczy',
            'characters': characters
        }
        if profile.character_status == 'gm':
            return render(request, 'characters/skills_sheets_for_gm.html', context)
        else:
            return redirect('home:dupa')


# class SkillsForGmListView(ListView):
#     context_object_name = 'characters'
#     queryset = Character.objects.all().select_related('profile')
#     template_name = 'characters/skills_sheets_for_gm.html'
#
#     @method_decorator(login_required)
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.profile.character_status != 'gm':
#             return redirect('home:dupa')
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context['page_title'] = 'Umiejętności graczy'
#         return context


# @query_debugger
# @login_required
# def tricks_view(request):
#     profile = request.user.profile
#
#     if profile.character_status == 'gm':
#         players_profiles = Profile.objects.exclude(Q(character_status='dead_player') |
#                                                    Q(character_status='living_npc') |
#                                                    Q(character_status='dead_npc') |
#                                                    Q(character_status='gm'))
#     else:
#         players_profiles = [profile]
#
#     context = {
#         'page_title': f'Podstępy - {profile.character_name}',
#         'players_profiles': players_profiles
#     }
#     return render(request, 'characters/character_tricks.html', context)


# @query_debugger
# @login_required
# def skills_sheet_view(request, profile_id='0'):
#     try:
#         profile = Profile.objects.get(id=profile_id)
#     except Profile.DoesNotExist:
#         profile = request.user.profile
#
#     skills = Skill.objects\
#         .filter(skill_levels__acquired_by_characters=profile.character)\
#         .exclude(name__icontains='Doktryn')\
#         .prefetch_related(Prefetch(
#             'skill_levels',
#             queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)
#         ))\
#         .distinct()
#
#     synergies = Synergy.objects\
#         .filter(synergy_levels__acquired_by_characters=profile.character) \
#         .prefetch_related(Prefetch(
#             'synergy_levels',
#             queryset=SynergyLevel.objects.filter(acquired_by_characters=profile.character)
#         )) \
#         .distinct()
#
#     context = {
#         'page_title': f'Umiejętności - {profile.character_name}',
#         'skills': skills,
#         'synergies': synergies,
#     }
#     if request.user.profile.character_status != 'gm' and profile_id != 0:
#         return redirect('home:dupa')
#     else:
#         return render(request, 'characters/skills_sheet.html', context)


# @query_debugger
# @login_required
# def skills_sheets_for_gm_view(request):
#     profile = request.user.profile
#     characters = Character.objects.all().select_related('profile')
#
#     context = {
#         'page_title': 'Umiejętności graczy',
#         'characters': characters
#     }
#     if profile.character_status == 'gm':
#         return render(request, 'characters/skills_sheets_for_gm.html', context)
#     else:
#         return redirect('home:dupa')

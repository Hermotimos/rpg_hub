from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from rpg_project.utils import query_debugger
from rules.models import Skill, Synergy, CharacterClass, CharacterProfession, EliteClass, EliteProfession, \
    WeaponClass, WeaponType, PlateType


@query_debugger
@login_required
def rules_main_view(request):
    context = {
        'page_title': 'Zasady'
    }
    return render(request, 'rules/main.html', context)


@query_debugger
@login_required
def rules_armor_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        plates = PlateType.objects.all().prefetch_related('pictures')
    else:
        plates = request.user.profile.allowed_plate_types.all().prefetch_related('pictures')

    context = {
        'page_title': 'Pancerz',
        'plates': plates
    }
    return render(request, 'rules/armor.html', context)


@query_debugger
@login_required
def rules_character_sheet_view(request):
    context = {
        'page_title': 'Karta postaci'
    }
    return render(request, 'rules/character_sheet.html', context)


@query_debugger
@login_required
def rules_combat_view(request):
    context = {
        'page_title': 'Przebieg walki'
    }
    return render(request, 'rules/combat.html', context)


@query_debugger
@login_required
def rules_masteries_view(request):
    context = {
        'page_title': 'Biegłości i inne zdolności bojowe'
    }
    return render(request, 'rules/masteries.html', context)


@query_debugger
@login_required
def rules_professions_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        classes = CharacterClass.objects.all().prefetch_related('professions')
        elite_classes = EliteClass.objects.all().prefetch_related('elite_professions')
    else:
        professions = CharacterProfession.objects\
            .filter(allowed_profiles=profile)
        classes = CharacterClass.objects\
            .filter(professions__allowed_profiles=profile)\
            .prefetch_related(Prefetch('professions', queryset=professions))\
            .distinct()
        elite_professions = EliteProfession.objects\
            .filter(allowed_profiles=profile)
        elite_classes = EliteClass.objects\
            .filter(allowed_profiles=profile)\
            .prefetch_related(Prefetch('elite_professions', queryset=elite_professions))

    context = {
        'page_title': 'Klasa, Profesja i rozwój postaci',
        'classes': classes,
        'elite_classes': elite_classes
    }
    return render(request, 'rules/professions.html', context)


@query_debugger
@login_required
def rules_skills_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        skills = Skill.objects.all()
        synergies = Synergy.objects.all().prefetch_related('skills')
    else:
        skills = request.user.profile.allowed_skills.all()
        synergies = request.user.profile.allowed_synergies.all().prefetch_related('skills')

    context = {
        'page_title': 'Umiejętności',
        'skills': skills,
        'synergies': synergies,
    }
    return render(request, 'rules/skills.html', context)


@query_debugger
@login_required
def rules_traits_view(request):
    context = {
        'page_title': 'Cechy'
    }
    return render(request, 'rules/traits.html', context)


@query_debugger
@login_required
def rules_tricks_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        plates = PlateType.objects.all()
    else:
        plates = request.user.profile.allowed_plate_types.all()

    context = {
        'page_title': 'Podstępy',
        'plates': plates
    }
    return render(request, 'rules/tricks.html', context)


@query_debugger
@login_required
def rules_weapons_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        weapon_classes = WeaponClass.objects.all().prefetch_related('weapon_types__pictures')
    else:
        weapon_types = WeaponType.objects.filter(allowed_profiles=profile).prefetch_related('pictures')
        weapon_classes = WeaponClass.objects.filter(weapon_types__allowed_profiles=profile)\
            .prefetch_related(Prefetch('weapon_types', queryset=weapon_types))

    context = {
        'page_title': 'Broń',
        'weapon_classes': weapon_classes
    }
    return render(request, 'rules/weapons.html', context)


@query_debugger
@login_required
def rules_wounds_view(request):
    context = {
        'page_title': 'Progi i skutki ran'
    }
    return render(request, 'rules/wounds.html', context)

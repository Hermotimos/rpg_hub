from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from rules.models import Skill, Synergy, CharacterClass, CharacterProfession, EliteClass, EliteProfession, \
    WeaponType, Weapon, Plate, Shield


@login_required
def rules_main_view(request):
    context = {
        'page_title': 'Zasady'
    }
    return render(request, 'rules/main.html', context)


@login_required
def rules_armor_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        plates = Plate.objects.all().prefetch_related('pictures')
        shields = Shield.objects.all().prefetch_related('pictures')
    else:
        plates = profile.allowed_plates.all().prefetch_related('pictures')
        shields = profile.allowed_shields.all().prefetch_related('pictures')

    context = {
        'page_title': 'Pancerz',
        'plates': plates,
        'shields': shields
    }
    return render(request, 'rules/armor.html', context)


@login_required
def rules_character_sheet_view(request):
    context = {
        'page_title': 'Karta postaci'
    }
    return render(request, 'rules/character_sheet.html', context)


@login_required
def rules_combat_view(request):
    context = {
        'page_title': 'Przebieg walki'
    }
    return render(request, 'rules/combat.html', context)


@login_required
def rules_masteries_view(request):
    context = {
        'page_title': 'Biegłości i inne zdolności bojowe'
    }
    return render(request, 'rules/masteries.html', context)


@login_required
def rules_professions_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        classes = CharacterClass.objects.all().prefetch_related('professions')
        elite_classes = EliteClass.objects.all().prefetch_related('elite_professions')
    else:
        professions = CharacterProfession.objects.filter(allowed_profiles=profile)
        classes = CharacterClass.objects\
            .filter(professions__allowed_profiles=profile)\
            .distinct()\
            .prefetch_related(Prefetch('professions', queryset=professions))

        elite_professions = EliteProfession.objects.filter(allowed_profiles=profile)
        elite_classes = EliteClass.objects\
            .filter(allowed_profiles=profile)\
            .prefetch_related(Prefetch('elite_professions', queryset=elite_professions))

    context = {
        'page_title': 'Klasa, Profesja i rozwój postaci',
        'classes': classes,
        'elite_classes': elite_classes
    }
    return render(request, 'rules/professions.html', context)


@login_required
def rules_skills_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        skills = Skill.objects.all().prefetch_related('skill_levels')
        synergies = Synergy.objects.all().prefetch_related('skills', 'synergy_levels')
    else:
        skills = profile.allowed_skills.all().prefetch_related('skill_levels')
        synergies = profile.allowed_synergies.all().prefetch_related('skills', 'synergy_levels')

    context = {
        'page_title': 'Umiejętności',
        'skills': skills,
        'synergies': synergies,
    }
    return render(request, 'rules/skills.html', context)


@login_required
def rules_traits_view(request):
    context = {
        'page_title': 'Cechy'
    }
    return render(request, 'rules/traits.html', context)


@login_required
def rules_tricks_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        plates = Plate.objects.all()
    else:
        plates = profile.allowed_plates.all()

    context = {
        'page_title': 'Podstępy',
        'plates': plates
    }
    return render(request, 'rules/tricks.html', context)


@login_required
def rules_weapons_view(request):
    profile = request.user.profile
    if profile.status == 'gm':
        weapon_classes = WeaponType.objects.all().prefetch_related('weapons__pictures')
    else:
        weapon_types = profile.allowed_weapons.prefetch_related('pictures')
        weapon_classes = WeaponType.objects\
            .filter(weapons__allowed_profiles=profile)\
            .distinct()\
            .prefetch_related(Prefetch('weapons', queryset=weapon_types))

    context = {
        'page_title': 'Broń',
        'weapon_classes': weapon_classes
    }
    return render(request, 'rules/weapons.html', context)


@login_required
def rules_wounds_view(request):
    context = {
        'page_title': 'Progi i skutki ran'
    }
    return render(request, 'rules/wounds.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rules.models import Skill, Synergy, CharacterClass, EliteClass, WeaponClass, WeaponType, PlateType


@login_required
def rules_main_view(request):
    context = {
        'page_title': 'Zasady'
    }
    return render(request, 'rules/main.html', context)


@login_required
def rules_skills_view(request):
    if request.user.profile.character_status == 'gm':
        skills = list(Skill.objects.all())
        synergies = list(Synergy.objects.all())
    else:
        skills = list(request.user.profile.allowed_skills.all())
        synergies = list(request.user.profile.allowed_synergies.all())

    context = {
        'page_title': 'Umiejętności',
        'skills': skills,
        'synergies': synergies,
    }
    return render(request, 'rules/skills.html', context)


@login_required
def rules_weapons_view(request):
    if request.user.profile.character_status == 'gm':
        weapons_classes_with_types_dict = \
            {wc: (wt for wt in wc.weapon_types.all()) for wc in WeaponClass.objects.all()}
    else:
        weapons_classes_with_types_dict = \
            {wc: (wt for wt in request.user.profile.allowed_weapon_types.all()) for wc in WeaponClass.objects.all()}

    context = {
        'page_title': 'Broń',
        'weapons_classes_with_types_dict': weapons_classes_with_types_dict
    }
    return render(request, 'rules/weapons.html', context)


@login_required
def rules_combat_view(request):
    context = {
        'page_title': 'Przebieg walki'
    }
    return render(request, 'rules/combat.html', context)


@login_required
def rules_traits_view(request):
    context = {
        'page_title': 'Cechy'
    }
    return render(request, 'rules/traits.html', context)


@login_required
def rules_masteries_view(request):
    context = {
        'page_title': 'Biegłości i inne zdolności bojowe'
    }
    return render(request, 'rules/masteries.html', context)


@login_required
def rules_tricks_view(request):
    if request.user.profile.character_status == 'gm':
        plates = list(PlateType.objects.all())
    else:
        plates = list(request.user.profile.allowed_plate_types.all())

    context = {
        'page_title': 'Podstępy',
        'plates': plates
    }
    return render(request, 'rules/tricks.html', context)


@login_required
def rules_wounds_view(request):
    context = {
        'page_title': 'Progi i skutki ran'
    }
    return render(request, 'rules/wounds.html', context)


@login_required
def rules_armor_view(request):
    if request.user.profile.character_status == 'gm':
        plates = list(PlateType.objects.all())
    else:
        plates = list(request.user.profile.allowed_plate_types.all())

    context = {
        'page_title': 'Pancerz',
        'plates': plates
    }
    return render(request, 'rules/armor.html', context)


@login_required
def rules_character_sheet_view(request):
    context = {
        'page_title': 'Karta postaci'
    }
    return render(request, 'rules/character_sheet.html', context)


@login_required
def rules_professions_view(request):
    if request.user.profile.character_status == 'gm':
        classes = list(CharacterClass.objects.all())
        classes_with_professions_dict = {c: [p for p in c.professions.all()] for c in classes}
        elite_classes = list(EliteClass.objects.all())
        elite_classes_with_professions_dict = {ec: [ep for ep in ec.elite_professions.all()] for ec in elite_classes}
    else:
        classes = list(c for c in CharacterClass.objects.all() if request.user.profile in c.allowed_list())
        classes_with_professions_dict = \
            {c: [p for p in c.professions.all() if request.user.profile in p.allowed_profiles.all()] for c in classes}
        elite_classes = list(ec for ec in EliteClass.objects.all() if request.user.profile in ec.allowed_profiles.all())
        elite_classes_with_professions_dict = \
            {ec: [ep for ep in ec.elite_professions.all() if request.user.profile in ep.allowed_profiles.all()]
             for ec in elite_classes}

    context = {
        'page_title': 'Klasa, Profesja i rozwój postaci',
        'classes_with_professions_dict': classes_with_professions_dict,
        'elite_classes': elite_classes,
        'elite_classes_with_professions_dict': elite_classes_with_professions_dict
    }
    return render(request, 'rules/professions.html', context)



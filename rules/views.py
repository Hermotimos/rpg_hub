from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rules.models import Skill, Synergy, CharacterClass, EliteClass


@login_required
def rules_main_view(request):
    context = {
        'page_title': 'Zasady'
    }
    return render(request, 'rules/main.html', context)


@login_required
def rules_skills_view(request):
    # for o in Skill.objects.all():
    #     o.save()
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
    context = {
        'page_title': 'Podstępy'
    }
    return render(request, 'rules/tricks.html', context)


@login_required
def rules_armor_view(request):
    context = {
        'page_title': 'Pancerz'
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
        elite_professions = list(EliteClass.objects.all())
    else:
        classes = list(c for c in CharacterClass.objects.all() if request.user.profile in c.allowed_list())
        classes_with_professions_dict = \
            {c: [p for p in c.professions.all() if request.user.profile in p.allowed_profiles.all()] for c in classes}
        elite_professions = list(p for p in EliteClass.objects.all() if request.user.profile in p.allowed_list())

    context = {
        'page_title': 'Klasa, Profesja i rozwój postaci',
        'classes_with_professions_dict': classes_with_professions_dict,
        'elite_professions': elite_professions
    }
    return render(request, 'rules/professions.html', context)



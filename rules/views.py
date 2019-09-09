from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rules.models import Skill, Synergy, CharacterClass, CharacterProfession


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
        'synergies': synergies
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
def rules_professions_view(request):
    classes = CharacterClass.objects.all()
    classes_with_professions_dict = {c: [p for p in c.professions.all()] for c in classes}

    context = {
        'page_title': 'Cechy',
        'classes_with_professions_dict': classes_with_professions_dict
    }
    return render(request, 'rules/professions.html', context)



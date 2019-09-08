from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rules.models import Skill, Synergy


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
    html = render(request, 'rules/combat.html', context).content
    html = str(html.decode('utf-8'))
    print(type(html))
    print(html)
    return render(request, 'rules/combat.html', context)

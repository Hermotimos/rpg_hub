from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404

from characters.models import Character
from rpg_project.utils import query_debugger
from rules.models import Skill, SkillLevel


@query_debugger
@login_required
def tricks_sheet_view(request):
    context = {
        'page_title': f'Podstępy - {request.user.profile.character_name}'
    }
    return render(request, 'characters/tricks_sheet.html', context)


@query_debugger
@login_required
def character_skills_view(request):
    profile = request.user.profile
    if profile.character_status == 'gm':
        characters = Character.objects.all().select_related('profile').prefetch_related('skill_levels_acquired__skill')
        # characters_with_skills_dict = {}
        # for ch in characters:
        #     characters_with_skills_dict[ch] = [s for s in ch.skill_levels_acquired.all()]
        skills = []
    else:
        skills = Skill.objects\
            .filter(skill_levels__acquired_by_characters=profile.character)\
            .prefetch_related(Prefetch(
                'skill_levels',
                queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)
            ))\
            .distinct()
        characters = []

    context = {
        'page_title': f'Umiejętności - {profile.character_name}',
        'characters': characters,
        'skills': skills
    }
    return render(request, 'characters/character_skills.html', context)

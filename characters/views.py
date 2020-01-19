from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404

from characters.models import Character
from knowledge.models import KnowledgePacket
from rpg_project.utils import query_debugger
from rules.models import Skill, SkillLevel, Synergy, SynergyLevel
from users.models import Profile


@query_debugger
@login_required
def tricks_sheet_view(request):
    context = {
        'page_title': f'Podstępy - {request.user.profile.character_name}'
    }
    return render(request, 'characters/tricks_sheet.html', context)


@query_debugger
@login_required
def skills_sheet_view(request, profile_id='0'):
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        profile = request.user.profile

    skills = Skill.objects\
        .filter(skill_levels__acquired_by_characters=profile.character)\
        .exclude(name__icontains='Doktryn')\
        .prefetch_related(Prefetch(
            'skill_levels',
            queryset=SkillLevel.objects.filter(acquired_by_characters=profile.character)
            .prefetch_related(Prefetch(
                'knowledge_packets',
                queryset=KnowledgePacket.objects.filter(allowed_profiles=profile)
                ))
        ))\
        .distinct()

    synergies = Synergy.objects\
        .filter(synergy_levels__acquired_by_characters=profile.character) \
        .prefetch_related(Prefetch(
            'synergy_levels',
            queryset=SynergyLevel.objects.filter(acquired_by_characters=profile.character)
            .prefetch_related(Prefetch(
                'knowledge_packets',
                queryset=KnowledgePacket.objects.filter(allowed_profiles=profile)
                ))
        )) \
        .distinct()

    knowledge_packets = KnowledgePacket.objects.all()
    context = {
        'page_title': f'Umiejętności - {profile.character_name}',
        'skills': skills,
        'synergies': synergies,
        'knowledge_packets': knowledge_packets
    }
    return render(request, 'characters/skills_sheet.html', context)


@query_debugger
@login_required
def skills_sheets_for_gm_view(request):
    characters = Character.objects.all().select_related('profile')
    context = {
        'page_title': 'Umiejętności graczy',
        'characters': characters
    }
    return render(request, 'characters/skills_sheets_for_gm.html', context)

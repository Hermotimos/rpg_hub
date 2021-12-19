from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect

from rules.models import Skill, SkillLevel, Synergy, SynergyLevel
from users.models import Profile


@login_required
def character_skills_view(request, profile_id='0'):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        profile = current_profile
    
    skills = Skill.objects.filter(skill_levels__acquired_by=profile)
    skills = skills.prefetch_related(
        Prefetch(
            'skill_levels',
            queryset=SkillLevel.objects.filter(acquired_by=profile)))
    
    synergies = Synergy.objects.filter(synergy_levels__acquired_by=profile)
    synergies = synergies.prefetch_related(
        Prefetch(
            'synergy_levels',
            queryset=SynergyLevel.objects.filter(acquired_by=profile)))
        
    context = {
        'current_profile': current_profile,
        'page_title': f'Umiejętności - {profile.character}',
        'skills': skills.distinct(),
        'synergies': synergies.distinct(),
    }
    if current_profile.status != 'gm' and profile_id != 0:
        return redirect('home:dupa')
    else:
        return render(request, 'development/character_skills.html', context)


@login_required
def character_skills_for_gm_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    profiles = Profile.players.all()
    
    context = {
        'current_profile': current_profile,
        'page_title': 'Umiejętności graczy',
        'profiles': profiles,
    }
    if current_profile.status == 'gm':
        return render(
            request, 'development/character_all_skills_for_gm.html', context)
    else:
        return redirect('home:dupa')


@login_required
def character_tricks_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    if current_profile.status == 'gm':
        players_profiles = Profile.players.filter(is_alive=True)
    else:
        players_profiles = [current_profile]
    
    context = {
        'current_profile': current_profile,
        'page_title': f'Podstępy - {current_profile.character}',
        'players_profiles': players_profiles
    }
    return render(request, 'development/character_tricks.html', context)


from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect

from contact.models import Plan
from rules.models import Profession, Klass, Skill, SkillLevel, Synergy, SynergyLevel
from users.models import Profile


@login_required
def profile_sheet_view(request, profile_id='0'):
    
    #  Character info
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        profile = request.user.profile
    try:
        pass
        # This won't work porperly untli Date model is ordered properly.
        # birth = profile.events_known_directly.order_by('date_start').first()
        # birthplace = birth.locations.first()
        # birthtime = f'{birth.date_start} {birth.in_timeunit.name_genetive}'
    except:
        birthplace = 'To skomplikowane...'
        birthtime = 'To skomplikowane...'

    # Professions tab
    profile_klasses = profile.profile_klasses.prefetch_related('levels__achievements')
    klasses = Klass.objects.filter(profile_klasses__in=profile_klasses)
    professions = Profession.objects.prefetch_related(
        Prefetch('klasses', queryset=klasses)
    )
    professions = professions.filter(klasses__in=klasses)
    professions = professions.distinct()
    
    # Skills tab
    skills = Skill.objects.filter(skill_levels__acquired_by=profile)
    skills = skills.exclude(name__icontains='Doktryn')
    skills = skills.prefetch_related(
        Prefetch(
            'skill_levels',
            queryset=SkillLevel.objects.filter(acquired_by=profile),
        )
    )
    skills = skills.distinct()

    synergies = Synergy.objects.filter(synergy_levels__acquired_by=profile)
    synergies = synergies.prefetch_related(
        Prefetch(
            'synergy_levels',
            queryset=SynergyLevel.objects.filter(acquired_by=profile),
        )
    )
    synergies = synergies.distinct()

    # print(professions)
    # print(profile_klasses)
   
    context = {
        'page_title': f'Karta postaci',
        'profile': profile,
        # 'birthplace': birthplace,
        # 'birthtime': birthtime,
        'professions': professions,
        'profile_klasses': profile_klasses,
        'skills': skills,
        'synergies': synergies,
    }
    if request.user.profile.status != 'gm' and profile_id == 0:
        return redirect('home:dupa')
    else:
        return render(request, 'development/profile_sheet.html', context)


@login_required
def character_skills_view(request, profile_id='0'):
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        profile = request.user.profile
    
    skills = Skill.objects \
        .filter(skill_levels__acquired_by=profile) \
        .exclude(name__icontains='Doktryn') \
        .prefetch_related(Prefetch(
        'skill_levels',
        queryset=SkillLevel.objects.filter(acquired_by=profile)
    )) \
        .distinct()
    
    synergies = Synergy.objects \
        .filter(synergy_levels__acquired_by=profile) \
        .prefetch_related(Prefetch(
        'synergy_levels',
        queryset=SynergyLevel.objects.filter(acquired_by=profile)
    )) \
        .distinct()
    
    context = {
        'page_title': f'Umiejętności - {profile.persona.name}',
        'skills': skills,
        'synergies': synergies,
    }
    if request.user.profile.status != 'gm' and profile_id != 0:
        return redirect('home:dupa')
    else:
        return render(request, 'development/character_skills.html', context)


@login_required
def character_skills_for_gm_view(request):
    profile = request.user.profile
    profiles = Profile.objects.filter(
        status__in=['active_player', 'inactive_player', 'dead_player']
    )
    
    context = {
        'page_title': 'Umiejętności graczy',
        'profiles': profiles,
    }
    if profile.status == 'gm':
        return render(request, 'development/character_all_skills_for_gm.html',
                      context)
    else:
        return redirect('home:dupa')


@login_required
def character_tricks_view(request):
    profile = request.user.profile
    
    if profile.status == 'gm':
        players_profiles = Profile.objects.exclude(
            Q(status='dead_player') | Q(status='living_npc')
            | Q(status='dead_npc') | Q(status='gm')
        )
    else:
        players_profiles = [profile]
    
    context = {
        'page_title': f'Podstępy - {profile.persona.name}',
        'players_profiles': players_profiles
    }
    return render(request, 'development/character_tricks.html', context)


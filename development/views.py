from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect

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
        birth = profile.events_known_directly.first()
        birthplace = birth.locations.first()
        birthtime = f'{birth.date_start} {birth.in_timeunit.name_genetive}'
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


    # XXXX tab
    
    
    context = {
        'page_title': f'Karta postaci',
        'profile': profile,
        'birthplace': birthplace,
        'birthtime': birthtime,
        'professions': professions,
        'profile_klasses': profile_klasses,
        'skills': skills,
        'synergies': synergies,
    }
    if request.user.profile.status != 'gm' and profile_id != 0:
        return redirect('home:dupa')
    else:
        return render(request, 'development/profile_sheet.html', context)

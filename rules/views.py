from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from rules.models import (
    EliteKlass,
    EliteProfession,
    Klass,
    Plate,
    Profession,
    Shield,
    Skill, SkillType,
    Synergy,
    WeaponType,
    Weapon,
)
from users.models import Profile


@login_required
def rules_main_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    context = {
        'current_profile': profile,
        'page_title': 'Zasady'
    }
    return render(request, 'rules/main.html', context)


@login_required
def rules_armor_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    if profile.can_view_all:
        plates = Plate.objects.all()
        shields = Shield.objects.all()
    else:
        plates = profile.allowed_plates.all()
        shields = profile.allowed_shields.all()

    context = {
        'current_profile': profile,
        'page_title': 'Pancerz',
        'plates': plates.prefetch_related('picture_sets__pictures'),
        'shields': shields.prefetch_related('picture_sets__pictures'),
    }
    return render(request, 'rules/armor.html', context)


@login_required
def rules_character_sheet_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': profile,
        'page_title': 'Karta Postaci'
    }
    return render(request, 'rules/character_sheet.html', context)


@login_required
def rules_combat_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': profile,
        'page_title': 'Przebieg walki'
    }
    return render(request, 'rules/combat.html', context)


@login_required
def rules_masteries_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': profile,
        'page_title': 'Biegłości i inne zdolności bojowe'
    }
    return render(request, 'rules/masteries.html', context)


@login_required
def rules_professions_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    if profile.can_view_all:
        professions = Profession.objects.all().prefetch_related('klasses')
        elite_professions = EliteProfession.objects.all().prefetch_related('elite_klasses')
    else:
        klasses = Klass.objects.filter(allowed_profiles=profile)
        professions = Profession.objects\
            .filter(klasses__allowed_profiles=profile)\
            .distinct()\
            .prefetch_related(Prefetch('klasses', queryset=klasses))

        elite_klasses = EliteKlass.objects.filter(allowed_profiles=profile)
        elite_professions = EliteProfession.objects\
            .filter(allowed_profiles=profile)\
            .prefetch_related(Prefetch('elite_klasses', queryset=elite_klasses))

    context = {
        'current_profile': profile,
        'page_title': 'Tworzenie Postaci, Klasa i Profesja',
        'professions': professions,
        'elite_professions': elite_professions
    }
    return render(request, 'rules/character_and_professions.html', context)


@login_required
def rules_skills_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Umiejętności',
    }
    return render(request, 'rules/skills.html', context)


@login_required
def rules_skills_list_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    if current_profile.can_view_all:
        skills = Skill.objects.filter(types__kinds__name="Powszechne")
        
    else:
        skills = Skill.objects.none()  # TODO temp, del when new Skills done
        # skills = profile.allowed_skills.filter(type__kinds__name="Powszechne")

    skills = skills.select_related('group__type')
    skills = skills.prefetch_related('skill_levels__perks__modifiers__factor')      # TODO del after changes?
    skills = skills.prefetch_related('skill_levels__perks__conditional_modifiers__conditions')
    skills = skills.prefetch_related('skill_levels__perks__conditional_modifiers__combat_types')
    skills = skills.prefetch_related('skill_levels__perks__conditional_modifiers__modifier__factor')
    skills = skills.prefetch_related('skill_levels__perks__comments')
    skills = skills.distinct()
    
    skill_types = SkillType.objects.filter(kinds__name='Powszechne')
    skill_types = skill_types.prefetch_related(Prefetch('skills', queryset=skills), 'skill_groups')
    skill_types = skill_types.filter(skills__in=skills).distinct()

    context = {
        'current_profile': current_profile,
        'page_title': 'Lista Umiejętności',
        'skill_types': skill_types,
        'skills': skills,
    }
    return render(request, 'rules/skills_list.html', context)


@login_required
def rules_synergies_list_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    if current_profile.can_view_all:
        synergies = Synergy.objects.prefetch_related('skills', 'synergy_levels')
    else:
        synergies = current_profile.allowed_synergies.prefetch_related('skills', 'synergy_levels')
        
    context = {
        'current_profile': current_profile,
        'page_title': 'Lista Synergii',
        'synergies': synergies,
    }
    return render(request, 'rules/synergies_list.html', context)


@login_required
def rules_traits_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': profile,
        'page_title': 'Cechy Fizyczne'
    }
    return render(request, 'rules/traits.html', context)


@login_required
def rules_tricks_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    if profile.can_view_all:
        plates = Plate.objects.all()
    else:
        plates = profile.allowed_plates.all()

    context = {
        'current_profile': profile,
        'page_title': 'Podstępy',
        'plates': plates,
    }
    return render(request, 'rules/tricks.html', context)


@login_required
def rules_weapons_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    
    if profile.can_view_all:
        weapon_types = WeaponType.objects.all()
        weapons = Weapon.objects.all()
    else:
        weapons = profile.allowed_weapons.all()
        weapon_types = WeaponType.objects.filter(
            weapons__allowed_profiles=profile).distinct()
    
    weapons = weapons.prefetch_related('picture_sets__pictures')
    weapon_types = weapon_types.prefetch_related(
        Prefetch('weapons', queryset=weapons))
    
    context = {
        'current_profile': profile,
        'page_title': 'Broń',
        'weapon_types': weapon_types,
    }
    return render(request, 'rules/weapons.html', context)


@login_required
def rules_wounds_view(request):
    profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': profile,
        'page_title': 'Progi i skutki ran'
    }
    return render(request, 'rules/wounds.html', context)

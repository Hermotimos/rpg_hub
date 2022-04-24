from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect

from rules.models import (
    Plate,
    Profession,
    PrimaryProfession,
    SecondaryProfession,
    Shield,
    Skill, SkillType,
    WeaponType,
    Weapon,
)
from rules.utils import get_overload_ranges, LOAD_LIMITS, get_user_professions, \
    can_view_special_rules
from users.models import Profile


@login_required
def rules_main_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()

    # Only Characters with specific Professions or a GM/Spectator can access some rules
    allowed_professions = ['Kapłan', 'Czarodziej', 'Teurg', 'Bard']
    if current_profile.status in ['gm', 'spectator']:
        user_professions_all = allowed_professions
        can_view_power_rules = True
    else:
        user_professions_all = get_user_professions(user_profiles)
        can_view_power_rules = can_view_special_rules(user_profiles, allowed_professions)
        
    context = {
        'current_profile': current_profile,
        'page_title': 'Zasady',
        'can_view_power_rules': can_view_power_rules,
        'user_professions_all': user_professions_all,
    }
    return render(request, 'rules/main.html', context)


@login_required
def rules_armor_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    
    plates = Plate.objects.filter(allowees__in=user_profiles).distinct()
    plates = plates.prefetch_related('picture_set__pictures__image')
    
    shields = Shield.objects.filter(allowees__in=user_profiles).distinct()
    shields = shields.prefetch_related('picture_set__pictures__image')
    
    context = {
        'current_profile': current_profile,
        'page_title': 'Pancerz',
        'plates': plates,
        'shields': shields,
    }
    return render(request, 'rules/armor.html', context)


@login_required
def rules_combat_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Przebieg walki'
    }
    return render(request, 'rules/combat.html', context)


@login_required
def rules_character_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Tworzenie Postaci, Klasa i Profesja',
    }
    return render(request, 'rules/character.html', context)


@login_required
def rules_professions_view(request, profession_type):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()

    if current_profile.can_view_all:
        primary_professions = PrimaryProfession.objects.filter(
            type=profession_type).prefetch_related('secondary_professions')
    else:
        secondary_professions = SecondaryProfession.objects.filter(
            allowees__in=user_profiles)
        primary_professions = Profession.objects.filter(
            type=profession_type, allowees__in=user_profiles)
        primary_professions = primary_professions.prefetch_related(
            Prefetch('secondary_professions', queryset=secondary_professions))

    context = {
        'current_profile': current_profile,
        'page_title': f'Klasy {profession_type}',
        'primary_professions': primary_professions.distinct(),
    }
    return render(request, 'rules/professions_list.html', context)


@login_required
def rules_skills_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Umiejętności',
    }
    return render(request, 'rules/skills.html', context)


@login_required
def rules_skills_list_view(request, skilltype_kind):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()

    if current_profile.can_view_all:
        skills = Skill.objects.filter(types__kinds__name=skilltype_kind)
    else:
        skills = Skill.objects.filter(allowees__in=user_profiles, types__kinds__name=skilltype_kind)
        
    skills = skills.select_related('group__type').distinct()
    skills = skills.prefetch_related(
        'skill_levels__perks__conditional_modifiers__conditions',
        'skill_levels__perks__conditional_modifiers__combat_types',
        'skill_levels__perks__conditional_modifiers__modifier__factor',
        'skill_levels__perks__comments',
    )

    skill_types = SkillType.objects.filter(kinds__name=skilltype_kind)
    skill_types = skill_types.prefetch_related(Prefetch('skills', queryset=skills), 'skill_groups')
    skill_types = skill_types.filter(skills__in=skills).distinct()
    
    context = {
        'current_profile': current_profile,
        'page_title': f'Umiejętności: {skilltype_kind}',
        'skilltype_kind': skilltype_kind,
        'skill_types': skill_types,
        'skills': skills,
    }
    return render(request, 'rules/skills_list.html', context)


@login_required
def rules_synergies_list_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Lista Synergii',
        'synergies': current_profile.synergies_allowed(),
    }
    return render(request, 'rules/synergies_list.html', context)


@login_required
def rules_traits_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Cechy Fizyczne'
    }
    return render(request, 'rules/traits.html', context)


@login_required
def rules_power_trait_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    context = {
        'current_profile': current_profile,
        'page_title': 'Moc'
    }
    if can_view_special_rules(user_profiles, ['Kapłan', 'Czarodziej', 'Teurg']):
        return render(request, 'rules/power_trait.html', context)
    else:
        return redirect('users:dupa')
    
    
@login_required
def rules_power_priests_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    context = {
        'current_profile': current_profile,
        'page_title': 'Moce Kapłańskie'
    }
    if can_view_special_rules(user_profiles, ['Kapłan']):
        return render(request, 'rules/power_priests.html', context)
    else:
        return redirect('users:dupa')
     
     
@login_required
def rules_power_sorcerers_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    context = {
        'current_profile': current_profile,
        'page_title': 'Magia'
    }
    if can_view_special_rules(user_profiles, ['Czarodziej']):
        return render(request, 'rules/power_sorcerers.html', context)
    else:
        return redirect('users:dupa')
    
     
@login_required
def rules_power_theurgists_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    context = {
        'current_profile': current_profile,
        'page_title': 'Teurgia'
    }
    if can_view_special_rules(user_profiles, ['Teurg']):
        return render(request, 'rules/power_theurgists.html', context)
    else:
        return redirect('users:dupa')


@login_required
def rules_tests_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    load_infos = [get_overload_ranges(v) for v in LOAD_LIMITS]
    context = {
        'current_profile': current_profile,
        'page_title': 'Testy Cech',
        'load_infos': load_infos,
    }
    return render(request, 'rules/tests.html', context)


@login_required
def rules_fitness_and_tricks_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Wydolność, Sprawności i Podstępy',
    }
    return render(request, 'rules/fitness_and_tricks.html', context)


@login_required
def rules_weapons_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    
    weapons = Weapon.objects.filter(allowees__in=user_profiles).distinct()
    weapons = weapons.prefetch_related('picture_set__pictures__image')
    weapon_types = WeaponType.objects.filter(weapons__allowees__in=user_profiles).distinct()
    weapon_types = weapon_types.prefetch_related(Prefetch('weapons', queryset=weapons))
    
    context = {
        'current_profile': current_profile,
        'page_title': 'Broń',
        'weapon_types': weapon_types,
    }
    return render(request, 'rules/weapons.html', context)


@login_required
def rules_wounds_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Progi i skutki ran'
    }
    return render(request, 'rules/wounds.html', context)


@login_required
def rules_character_sheet_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Karta Postaci'
    }
    return render(request, 'rules/character_sheet.html', context)


@login_required
def rules_experience_demand_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Sztuka kompozycji Dezyderatu Expowego'
    }
    return render(request, 'rules/experience_demand.html', context)

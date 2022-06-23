from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect

from rules.models import (
    Plate,
    Profession,
    SubProfession,
    Shield,
    Skill, SkillType,
    WeaponType,
)
from rules.utils import get_overload_ranges, get_own_professions, \
    can_view_special_rules, get_overload_ranges2
from users.models import Profile


@login_required
def rules_main_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    
    # Only Characters with specific Professions or a GM/Spectator can access some rules
    elite_professions = [
        p.name for p in Profession.objects.filter(type='Elitarne')]
    
    if current_profile.status in ['gm', 'spectator']:
        own_professions = elite_professions
        can_view_power_rules = True
    else:
        own_professions = get_own_professions(current_profile)
        can_view_power_rules = can_view_special_rules(current_profile, elite_professions)

    context = {
        'current_profile': current_profile,
        'page_title': 'Zasady',
        'can_view_power_rules': can_view_power_rules,
        'own_professions': own_professions,
    }
    return render(request, 'rules/main.html', context)


@login_required
def rules_armor_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    
    plates = Plate.objects.prefetch_related('picture_set__pictures__image')
    shields = Shield.objects.prefetch_related('picture_set__pictures__image')
    
    if not current_profile.can_view_all:
        plates = plates.filter(allowees__in=user_profiles)
        shields = shields.filter(allowees__in=user_profiles)
    
    context = {
        'current_profile': current_profile,
        'page_title': 'Pancerz',
        'plates': plates.distinct(),
        'shields': shields.distinct(),
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

    professions = Profession.objects.filter(type=profession_type)
    subprofessions = SubProfession.objects.all()
    essential_skills = Skill.objects.filter()

    if not current_profile.can_view_all:
        professions = professions.filter(allowees__in=user_profiles)
        subprofessions = subprofessions.filter(allowees__in=user_profiles)
        essential_skills = Skill.objects.filter(allowees__in=user_profiles).distinct()

    subprofessions = subprofessions.prefetch_related(
        Prefetch('essential_skills', queryset=essential_skills)).distinct()
    professions = professions.prefetch_related(
        Prefetch('subprofessions', queryset=subprofessions))

    context = {
        'current_profile': current_profile,
        'page_title': f'Klasy {profession_type}',
        'professions': professions.distinct(),
    }
    return render(request, 'rules/professions.html', context)


@login_required
def rules_character_development_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Rozwój Postaci',
    }
    return render(request, 'rules/character_development.html', context)


@login_required
def rules_skills_view(request, skilltype_kind):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()

    skills_regular = Skill.objects.filter(
        types__kinds__name=skilltype_kind, version_of=None)
    
    if not current_profile.can_view_all:
        skills_regular = skills_regular.filter(allowees__in=user_profiles)
        
    skills_regular = skills_regular.select_related('group__type')
    skills_regular = skills_regular.prefetch_related(
        'skill_levels__perks__conditional_modifiers__conditions',
        'skill_levels__perks__conditional_modifiers__combat_types',
        'skill_levels__perks__conditional_modifiers__modifier__factor',
        'skill_levels__perks__comments',
    ).distinct()

    skill_types_regular = SkillType.objects.filter(kinds__name=skilltype_kind)
    skill_types_regular = skill_types_regular.prefetch_related(
        Prefetch('skills', queryset=skills_regular), 'skill_groups')
    skill_types_regular = skill_types_regular.filter(skills__in=skills_regular).distinct()
    
    context = {
        'current_profile': current_profile,
        'page_title': f"Umiejętności {skilltype_kind}",
        'skilltype_kind': skilltype_kind,
        'skill_types_regular': skill_types_regular,
        'skills_regular': skills_regular,
    }
    return render(request, 'rules/skills.html', context)


@login_required
def rules_synergies_view(request, skilltype_kind="Powszechne"):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': f"Synergie {skilltype_kind}",
        'synergies': current_profile.synergies_allowed(skilltype_kind=skilltype_kind),
    }
    return render(request, 'rules/synergies.html', context)


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
    context = {
        'current_profile': current_profile,
        'page_title': 'Moc'
    }
    if can_view_special_rules(current_profile, ['Kapłan', 'Czarodziej', 'Teurg']):
        return render(request, 'rules/power_trait.html', context)
    else:
        return redirect('users:dupa')
    
    
@login_required
def rules_priesthood_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Kapłaństwo',
    }
    if can_view_special_rules(current_profile, ['Kapłan']):
        return render(request, 'rules/priesthood.html', context)
    else:
        return redirect('users:dupa')
     
     
@login_required
def rules_sorcery_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Magia',
    }
    if can_view_special_rules(current_profile, ['Czarodziej']):
        return render(request, 'rules/sorcery.html', context)
    else:
        return redirect('users:dupa')
    
     
@login_required
def rules_theurgy_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Teurgia',
    }
    if can_view_special_rules(current_profile, ['Teurg']):
        return render(request, 'rules/theurgy.html', context)
    else:
        return redirect('users:dupa')


@login_required
def rules_tests_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    load_infos = get_overload_ranges()
    load_infos2 = get_overload_ranges2()
    context = {
        'current_profile': current_profile,
        'page_title': 'Testy Cech',
        'load_infos': load_infos,
        'load_infos2': load_infos2,
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
def rules_weapon_types_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    
    weapon_types = WeaponType.objects.prefetch_related(
        'picture_set__pictures__image',
        'damage_types',
        'comparables')
    if not current_profile.can_view_all:
        weapon_types = weapon_types.filter(allowees__in=user_profiles)

    context = {
        'current_profile': current_profile,
        'page_title': 'Broń',
        'weapon_types': weapon_types.distinct(),
    }
    return render(request, 'rules/weapon_types.html', context)


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

from collections import namedtuple
from typing import Tuple

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
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Zasady'
    }
    return render(request, 'rules/main.html', context)


@login_required
def rules_armor_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()
    
    plates = Plate.objects.filter(allowees__in=user_profiles).distinct()
    shields = Shield.objects.filter(allowees__in=user_profiles).distinct()
    
    context = {
        'current_profile': current_profile,
        'page_title': 'Pancerz',
        'plates': plates.prefetch_related('picture_sets__pictures'),
        'shields': shields.prefetch_related('picture_set__pictures'),
    }
    return render(request, 'rules/armor.html', context)


@login_required
def rules_character_sheet_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Karta Postaci'
    }
    return render(request, 'rules/character_sheet.html', context)


@login_required
def rules_combat_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    context = {
        'current_profile': current_profile,
        'page_title': 'Przebieg walki'
    }
    return render(request, 'rules/combat.html', context)


@login_required
def rules_professions_view(request):
    current_profile = Profile.objects.get(id=request.session['profile_id'])
    user_profiles = current_profile.user.profiles.all()

    klasses = Klass.objects.filter(allowees__in=user_profiles).distinct()
    professions = Profession.objects.filter(klasses__allowees__in=user_profiles)
    professions = professions.prefetch_related(Prefetch('klasses', queryset=klasses)).distinct()

    elite_klasses = EliteKlass.objects.filter(allowees__in=user_profiles).distinct()
    elite_professions = EliteProfession.objects.filter(allowees__in=user_profiles)
    elite_professions = elite_professions.prefetch_related(Prefetch('elite_klasses', queryset=elite_klasses)).distinct()

    context = {
        'current_profile': current_profile,
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
    user_profiles = current_profile.user.profiles.all()

    skills = Skill.objects.filter(allowees__in=user_profiles, types__kinds__name="Powszechne")
    skills = skills.select_related('group__type').distinct()
    skills = skills.prefetch_related(
        'skill_levels__perks__conditional_modifiers__conditions',
        'skill_levels__perks__conditional_modifiers__combat_types',
        'skill_levels__perks__conditional_modifiers__modifier__factor',
        'skill_levels__perks__comments',
    )
    
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
    user_profiles = current_profile.user.profiles.all()

    synergies = Synergy.objects.filter(allowees__in=user_profiles)
    synergies = synergies.prefetch_related(
        'skills',
        'synergy_levels__perks__conditional_modifiers__conditions',
        'synergy_levels__perks__conditional_modifiers__combat_types',
        'synergy_levels__perks__conditional_modifiers__modifier__factor',
        'synergy_levels__perks__comments',
    )
    synergies = synergies.distinct()

    context = {
        'current_profile': current_profile,
        'page_title': 'Lista Synergii',
        'synergies': synergies,
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


LOAD_LIMITS = [
    [0, 3],
    [2, 6],
    [3, 10],
    [6, 15],
    [9, 22],
    [12, 25],
    [15, 28],
    [18, 35],
    [20, 45],
    [20, 57],
    [20, 62],
    [23, 70],
    [24, 75],
    [27, 85],
    [30, 90],
    [35, 98],
    [40, 110],
    [55, 128],
    [68, 140],
    [80, 153]
]


def get_overload_ranges(vals: Tuple[int, int]) -> namedtuple:
    load_regular, load_max = vals
    third = (load_max - load_regular) // 3
    overload_1 = f"{load_regular+1} - {load_regular+third}"
    overload_2 = f"{load_regular+1+third} - {load_regular+third*2}"
    overload_3 = f"{min(load_regular+1+third*2, load_max-1)} - {load_max-1}"
    LoadInfo = namedtuple(
        'LoadInfo',
        ['load_regular', 'load_max', 'overload_1', 'overload_2', 'overload_3'])
    return LoadInfo(load_regular, load_max, overload_1, overload_2, overload_3)


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
    weapons = weapons.prefetch_related('picture_sets__pictures')
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

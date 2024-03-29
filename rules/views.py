from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, redirect

from rpg_project.utils import auth_profile
from rules.models import (
    Plate,
    Profession,
    SubProfession,
    Shield,
    Skill, SkillType,
    WeaponType,
    Sphere, PriestSpell, TheurgistSpell, SorcererSpell,
)
from rules.utils import get_overload_ranges, get_visible_professions, \
    can_view_special_rules, get_wounds_range_sets


@login_required
@auth_profile(['all'])
def rules_main_view(request):
    current_profile = request.current_profile

    # Only Characters with specific Professions or a GM/Spectator can access some rules
    elite_professions = [p.name for p in Profession.objects.filter(type='Elitarne')]

    if current_profile.status in ['gm', 'spectator']:
        visible_professions = elite_professions
        can_view_power_rules = True
    else:
        visible_professions = get_visible_professions(current_profile)
        can_view_power_rules = can_view_special_rules(current_profile, elite_professions)

    context = {
        'page_title': 'Zasady',
        'can_view_power_rules': can_view_power_rules,
        'visible_professions': visible_professions,
    }
    return render(request, 'rules/main.html', context)


@login_required
@auth_profile(['all'])
def rules_armor_view(request):
    current_profile = request.current_profile
    user_profiles = current_profile.user.profiles.all()

    plates = Plate.objects.prefetch_related('picture_set__pictures__image')
    shields = Shield.objects.prefetch_related('picture_set__pictures__image')

    if not current_profile.can_view_all:
        plates = plates.filter(allowees__in=user_profiles)
        shields = shields.filter(allowees__in=user_profiles)

    context = {
        'page_title': 'Pancerz',
        'plates': plates.distinct(),
        'shields': shields.distinct(),
    }
    return render(request, 'rules/armor.html', context)


@login_required
@auth_profile(['all'])
def rules_combat_view(request):
    context = {
        'page_title': 'Przebieg walki'
    }
    return render(request, 'rules/combat.html', context)


@login_required
@auth_profile(['all'])
def rules_character_view(request):
    context = {
        'page_title': 'Tworzenie Postaci, Klasa i Profesja',
    }
    return render(request, 'rules/character.html', context)


@login_required
@auth_profile(['all'])
def rules_professions_view(request, profession_type):
    current_profile = request.current_profile
    user_profiles = current_profile.user.profiles.all()

    professions = Profession.objects.filter(type=profession_type)
    subprofessions = SubProfession.objects.all()
    essential_skills = Skill.objects.all()

    if not current_profile.can_view_all:
        professions = professions.filter(allowees__in=user_profiles)
        subprofessions = subprofessions.filter(allowees__in=user_profiles)
        essential_skills = essential_skills.filter(allowees__in=user_profiles).distinct()

    subprofessions = subprofessions.prefetch_related(
        Prefetch('essential_skills', queryset=essential_skills)
    ).distinct()

    professions = professions.prefetch_related(
        Prefetch('subprofessions', queryset=subprofessions)
    ).distinct()

    context = {
        'page_title': f'Klasy {profession_type}',
        'professions': professions.distinct(),
    }
    return render(request, 'rules/professions.html', context)


@login_required
@auth_profile(['all'])
def rules_character_development_view(request):
    context = {
        'page_title': 'Rozwój Postaci',
    }
    return render(request, 'rules/character_development.html', context)


@login_required
@auth_profile(['all'])
def rules_skills_view(request, skilltype_kind):
    current_profile = request.current_profile
    user_profiles = current_profile.user.profiles.all()

    skills = Skill.objects.filter(
        types__kinds__name=skilltype_kind
    ).prefetch_related(
        'skill_levels__perks__conditional_modifiers__conditions',
        'skill_levels__perks__conditional_modifiers__combat_types',
        'skill_levels__perks__conditional_modifiers__modifier__factor',
        'skill_levels__perks__comments',
    ).select_related(
        'group__type'
    ).distinct()

    if not current_profile.can_view_all:
        skills = skills.filter(allowees__in=user_profiles)

    skill_types = SkillType.objects.prefetch_related(
        Prefetch('skills', queryset=skills), 'skill_groups',
    ).filter(
        skills__in=skills
    ).distinct()

    if skilltype_kind in ["Powszechne", "Mentalne"]:
        page_title = f"Umiejętności {skilltype_kind}"
    else:
        page_title = skilltype_kind

    context = {
        'page_title': page_title,
        'skilltype_kind': skilltype_kind,
        'skill_types': skill_types,
        'skills': skills,
    }
    return render(request, 'rules/skills.html', context)


@login_required
@auth_profile(['all'])
def rules_synergies_view(request, skilltype_kind):
    current_profile = request.current_profile

    synergies = current_profile.synergies_allowed(
        skilltype_kind=skilltype_kind
    ).distinct()

    context = {
        'page_title': f"Synergie {skilltype_kind}",
        'skilltype_kind': skilltype_kind,
        'synergies': synergies,
    }
    return render(request, 'rules/synergies.html', context)


@login_required
@auth_profile(['all'])
def rules_traits_view(request):
    context = {
        'page_title': 'Cechy Fizyczne'
    }
    return render(request, 'rules/traits.html', context)


@login_required
@auth_profile(['all'])
def rules_power_trait_view(request):
    current_profile = request.current_profile
    context = {
        'page_title': 'Moc'
    }
    if can_view_special_rules(current_profile, ['Kapłan', 'Czarodziej', 'Teurg']):
        return render(request, 'rules/power_trait.html', context)
    else:
        return redirect('users:dupa')


@login_required
@auth_profile(['all'])
def rules_priesthood_view(request):
    current_profile = request.current_profile
    context = {
        'page_title': 'Kapłaństwo',
    }
    if can_view_special_rules(current_profile, ['Kapłan']):
        return render(request, 'rules/priesthood.html', context)
    else:
        return redirect('users:dupa')


@login_required
@auth_profile(['all'])
def rules_sorcery_view(request):
    current_profile = request.current_profile
    context = {
        'page_title': 'Magia',
    }
    if can_view_special_rules(current_profile, ['Czarodziej']):
        return render(request, 'rules/sorcery.html', context)
    else:
        return redirect('users:dupa')


@login_required
@auth_profile(['all'])
def rules_theurgy_view(request):
    current_profile = request.current_profile
    context = {
        'page_title': 'Teurgia',
    }
    if can_view_special_rules(current_profile, ['Teurg']):
        return render(request, 'rules/theurgy.html', context)
    else:
        return redirect('users:dupa')


@login_required
@auth_profile(['all'])
def rules_tests_view(request):
    context = {
        'page_title': 'Testy Cech',
        'load_infos': get_overload_ranges(),
    }
    return render(request, 'rules/tests.html', context)


@login_required
@auth_profile(['all'])
def rules_fitness_and_tricks_view(request):
    context = {
        'page_title': 'Wydolność, Sprawności i Podstępy',
    }
    return render(request, 'rules/fitness_and_tricks.html', context)


@login_required
@auth_profile(['all'])
def rules_weapon_types_view(request):
    current_profile = request.current_profile
    user_profiles = current_profile.user.profiles.all()

    weapon_types = WeaponType.objects.all()
    if not current_profile.can_view_all:
        weapon_types = weapon_types.filter(allowees__in=user_profiles).distinct()

    weapon_types = weapon_types.prefetch_related(
        Prefetch('comparables', queryset=weapon_types),  # filter out unknown
        'picture_set__pictures__image',
        'damage_types'
    ).distinct()

    context = {
        'page_title': 'Broń',
        'weapon_types': weapon_types,
    }
    return render(request, 'rules/weapon_types.html', context)


@login_required
@auth_profile(['all'])
def rules_wounds_view(request):
    context = {
        'page_title': 'Progi i skutki ran',
        'wounds_range_sets': get_wounds_range_sets(),
    }
    return render(request, 'rules/wounds.html', context)


@login_required
@auth_profile(['all'])
def rules_character_sheet_view(request):
    context = {
        'page_title': 'Karta Postaci'
    }
    return render(request, 'rules/character_sheet.html', context)


@login_required
@auth_profile(['all'])
def rules_experience_demand_view(request):
    context = {
        'page_title': 'Sztuka kompozycji Dezyderatu Expowego'
    }
    return render(request, 'rules/experience_demand.html', context)


@login_required
@auth_profile(['all'])
def rules_player_responsibilities_view(request):
    context = {
        'page_title': 'Obowiązki Gracza'
    }
    return render(request, 'rules/player_responsibilities.html', context)


# =============================================================================


@login_required
@auth_profile(['all'])
def rules_spells_view(request, spells_kind):
    current_profile = request.current_profile
    user_profiles = current_profile.user.profiles.all()

    models = {
        'Moce Kapłańskie': PriestSpell,
        'Moce Teurgiczne': TheurgistSpell,
        'Zaklęcia': SorcererSpell,
    }
    SpellModel = models.get(spells_kind)
    print(1111, SpellModel.__name__)

    spells = SpellModel.objects.prefetch_related('spheres', 'domains', 'allowees')
    if not current_profile.can_view_all:
        spells = spells.filter(allowees__in=user_profiles)

    spheres = Sphere.objects.prefetch_related(
        Prefetch('spells', queryset=spells)
    ).filter(spells__in=spells).distinct()

    context = {
        'page_title': spells_kind,
        'spells_kind': spells_kind,
        'spheres': spheres,
        'spells': spells,
    }
    return render(request, 'rules/spells.html', context)

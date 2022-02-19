from collections import namedtuple
from typing import Tuple

from django.db.models import Prefetch, Q

import users
from rules.models import Synergy, Skill, SkillLevel, SynergyLevel


def can_view_enchanting_rules(user_profiles):
    allowed_profiles = user_profiles.filter(Q(status='gm') | Q(is_enchanter=True))
    return allowed_profiles.exists()


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


def get_synergies_allowed(user_profiles):
    """Get synergies whose all composing skills are allowed to any od user's profiles."""
    skills = Skill.objects.filter(allowees__in=user_profiles)
    synergies = Synergy.objects.prefetch_related(
        'skills',
        'synergy_levels__skill_levels__skill',
        'synergy_levels__perks__conditional_modifiers__conditions',
        'synergy_levels__perks__conditional_modifiers__combat_types',
        'synergy_levels__perks__conditional_modifiers__modifier__factor',
        'synergy_levels__perks__comments',
    )
    return [
        synergy for synergy in synergies
        if all([(skill in skills) for skill in synergy.skills.all()])
    ]


def get_synergies_acquired(profile: users.models.Profile):
    skill_levels = SkillLevel.objects.filter(acquired_by=profile)
    
    synergy_levels = SynergyLevel.objects.prefetch_related('skill_levels')
    synergy_levels_ids = [
        synergy_lvl.id for synergy_lvl in synergy_levels
        if all([(skill_lvl in skill_levels) for skill_lvl in synergy_lvl.skill_levels.all()])
    ]
    
    synergy_levels = SynergyLevel.objects.filter(id__in=synergy_levels_ids)
    synergy_levels = synergy_levels.prefetch_related(
        'synergy__skills',
        'perks__conditional_modifiers__conditions',
        'perks__conditional_modifiers__combat_types',
        'perks__conditional_modifiers__modifier__factor',
        'perks__comments',
        'skill_levels__skill',
    )
    synergies = Synergy.objects.filter(synergy_levels__in=synergy_levels)
    synergies = synergies.prefetch_related(Prefetch('synergy_levels', queryset=synergy_levels))
    return synergies

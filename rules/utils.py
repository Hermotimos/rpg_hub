from collections import namedtuple
from typing import Tuple
import users
from rules.models import Synergy, Skill


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
    pass


    # TODO delete allowees field on Synergy
    # TODO after depoying to production reload GM allowed (after migration)
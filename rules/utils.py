from collections import namedtuple
from typing import Tuple


def get_user_professions(user_profiles):
    user_professions_all = []
    for profile in user_profiles.prefetch_related('character__professions'):
        user_professions_all.extend(
            [p.name for p in profile.character.professions.all()])
    return user_professions_all


def can_view_special_rules(user_profiles, allowed_professions):
    if user_profiles.filter(status__in=['gm', 'spectator']):
        return True
    else:
        user_professions_all = get_user_professions(user_profiles)
        return any(
            [profession in allowed_professions for profession in user_professions_all]
        )


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

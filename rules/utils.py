from collections import namedtuple
from typing import Tuple

from prosoponomikon.models import Character
from rules.models import Profession, SubProfession


def get_own_professions(current_profile):
    user_profiles = current_profile.user.profiles.all()
    subprofessions = SubProfession.objects.filter(
        characters__in=Character.objects.filter(profile__in=user_profiles))
    allowed_professions = Profession.objects.filter(
        subprofessions__in=subprofessions)
    return [p.name for p in allowed_professions]


def can_view_special_rules(current_profile, restricted_professions):
    user_profiles = current_profile.user.profiles.all()
    if user_profiles.filter(status__in=['gm', 'spectator']):
        return True
    else:
        allowed_professions = get_own_professions(current_profile)
        return any([p in restricted_professions for p in allowed_professions])


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


def get_overload_ranges() -> namedtuple:
    
    def _get_overload_ranges(vals: Tuple[int, int]) -> namedtuple:
        load_regular, load_max = vals
        third = (load_max - load_regular) // 3
        overload_1 = f"{load_regular + 1} - {load_regular + third}"
        overload_2 = f"{load_regular + 1 + third} - {load_regular + third * 2}"
        overload_3 = f"{min(load_regular + 1 + third * 2, load_max - 1)} - {load_max - 1}"
        LoadInfo = namedtuple(
            'LoadInfo',
            ['load_regular', 'load_max', 'overload_1', 'overload_2',
             'overload_3'])
        return LoadInfo(load_regular, load_max, overload_1, overload_2, overload_3)
    
    return [_get_overload_ranges(v) for v in LOAD_LIMITS]
    

LOAD_LIMITS2 = [
    [1, 0],
    [2, 2],
    [3, 3],
    [4, 6],
    [5, 9],
    [6, 12],
    [7, 15],
    [8, 16],
    [9, 18],
    [10, 20],
    [11, 21],
    [12, 24],
    [12, 26],
    [14, 29],
    [15, 32],
    [16, 37],
    [17, 42],
    [18, 56],
    [19, 70],
    [20, 85]
]


def get_overload_ranges2() -> namedtuple:
    
    def _get_overload_ranges(vals: Tuple[int, int]) -> namedtuple:
        strength, load_regular = vals
        overload_1 = f"{load_regular + 1} - {load_regular + strength}"
        overload_2 = f"{load_regular + strength + 1} - {load_regular + strength*2}"
        overload_3 = f"{load_regular + strength*2 + 1} - {load_regular + strength*3}"
        overload_4 = f"{load_regular + strength*3 + 1} - {load_regular + strength*4}"
        LoadInfo = namedtuple(
            'LoadInfo',
            ['load_regular', 'overload_1', 'overload_2', 'overload_3', 'overload_4'])
        return LoadInfo(
            load_regular, overload_1, overload_2, overload_3, overload_4)
    
    return [_get_overload_ranges(v) for v in LOAD_LIMITS2]

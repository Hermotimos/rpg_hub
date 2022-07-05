from collections import namedtuple
from math import floor, ceil
from typing import Tuple

from prosoponomikon.models import Character
from rules.models import Profession, SubProfession


# -----------------------------------------------------------------------------


def get_visible_professions(current_profile):
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
        allowed_professions = get_visible_professions(current_profile)
        return any([p in restricted_professions for p in allowed_professions])


# -----------------------------------------------------------------------------


LOAD_LIMITS = [
    [1, 0],
    [2, 2],
    [3, 3],
    [4, 6],
    [5, 9],
    [6, 12],
    [7, 14],
    [8, 16],
    [9, 18],
    [10, 20],
    [11, 22],
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


def get_overload_ranges() -> namedtuple:
    
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
    
    return [_get_overload_ranges(v) for v in LOAD_LIMITS]


# -----------------------------------------------------------------------------


HEALTH_VALUES = range(1, 51)


def get_wounds_ranges() -> namedtuple:
    
    def simplify_false_ranges(text: str):
        """Convert range with bottom identical to top, ex. "2 - 2" -> "2"."""
        bottom, top = text.split(" - ")
        if bottom == top:
            return bottom
        return text
        
    def _get_wounds_ranges(health: int) -> namedtuple:
        WoundsRanges = namedtuple(
            'WoundsRanges', ['health', 'light', 'medium', 'heavy', 'deadly'])

        if health <= 2:
            return WoundsRanges(health, "-", "-", "-", "1+")
        elif health == 3:
            return WoundsRanges(health, "-", "-", "1", "2+")
        elif health == 4:
            return WoundsRanges(health, "-", "1", "2", "3+")
        else:
            if health < 17:
                light_bottom = health // 7
                light_top = light_bottom + 1
            elif health < 23:
                light_bottom = health // 7
                light_top = light_bottom + max(floor(health % 7 / 2 - 1), 1)
            elif health < 34:
                light_bottom = health // 6
                light_top = light_bottom + max(floor(health % 6 / 2), 1)
            else:
                light_bottom = health // 6 + 1
                light_top = light_bottom + max(floor(health % 6 / 2), 1)

            light = simplify_false_ranges(f"{min(max(light_bottom, 1), 10)} - {light_top}")
            
            medium_bottom = light_top + 1
            medium_top = medium_bottom + health // 9
            medium = simplify_false_ranges(f"{medium_bottom} - {medium_top}")
            
            heavy_bottom = medium_top + 1
            heavy_top = heavy_bottom + health // 9
            heavy = simplify_false_ranges(f"{heavy_bottom} - {heavy_top}")
            
            deadly = f"{heavy_top + 1}+"
    
        return WoundsRanges(health, light, medium, heavy, deadly)

    return [_get_wounds_ranges(v) for v in HEALTH_VALUES]


# -----------------------------------------------------------------------------

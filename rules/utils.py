from collections import namedtuple
from dataclasses import dataclass
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
        return LoadInfo(load_regular, overload_1, overload_2, overload_3, overload_4)
    
    return [_get_overload_ranges(v) for v in LOAD_LIMITS]


# -----------------------------------------------------------------------------


def construct_range_str(bottom, top):
    if bottom > top or top == 0:
        return '-'
    if bottom == 0:
        return f"{top}"
    if bottom == top:
        return f"{bottom}"
    return f"{bottom}-{top}"


@dataclass(frozen=True)
class WoundsRangeSet:
    health: int

    @property
    def deadly_bottom(self):
        if self.health == 1:
            return 1
        if self.health < 30:
            return self.health // 2
        return (self.health // 2) + (self.health // 10) - 2

    @property
    def light_bottom(self):
        return self.deadly_bottom // 3
    
    @property
    def interval(self):
        return (self.deadly_bottom - self.light_bottom) // 3

    @property
    def medium_bottom(self):
        return self.light_bottom + self.interval

    @property
    def heavy_bottom(self):
        return self.medium_bottom + self.interval

    @property
    def light_top(self):
        return self.medium_bottom - 1

    @property
    def medium_top(self):
        return self.heavy_bottom - 1

    @property
    def heavy_top(self):
        return self.deadly_bottom - 1

    @property
    def light_wounds(self):
        return construct_range_str(self.light_bottom, self.light_top)

    @property
    def medium_wounds(self):
        return construct_range_str(self.medium_bottom, self.medium_top)

    @property
    def heavy_wounds(self):
        return construct_range_str(self.heavy_bottom, self.heavy_top)
    
    @property
    def deadly_wounds(self):
        return f"{self.deadly_bottom}+"
    

def get_wounds_range_sets() -> namedtuple:
    return [WoundsRangeSet(val) for val in range(1, 51)]


# -----------------------------------------------------------------------------

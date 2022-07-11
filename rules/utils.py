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


@dataclass(frozen=True)
class OverLoadRangeSet:
    base_load: int

    @property
    def interval(self):
        if self.base_load < 30:
            return self.base_load / 2
        return self.base_load / 2 - (self.base_load / 20)

    def get_top(self, overload_lvl):
        return int(self.base_load + (self.interval * overload_lvl))

    def get_bottom(self, overload_lvl):
        return int(self.get_top(overload_lvl-1) + 1)
    
    @staticmethod
    def get_overload_range_str(bottom, top):
        if bottom > top or top == 0:
            return '-'
        if bottom >= top:
            return f"{bottom}"
        return f"{bottom}-{top}"

    @property
    def overload_1(self):
        return self.get_overload_range_str(self.get_bottom(1), self.get_top(1))
     
    @property
    def overload_2(self):
        return self.get_overload_range_str(self.get_bottom(2), self.get_top(2))
     
    @property
    def overload_3(self):
        return self.get_overload_range_str(self.get_bottom(3), self.get_top(3))
     
    @property
    def overload_4(self):
        return self.get_overload_range_str(self.get_bottom(4), self.get_top(4))
     
     
def get_overload_ranges():
    return [OverLoadRangeSet(val) for val in range(1, 61)]


# -----------------------------------------------------------------------------


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

    @staticmethod
    def get_wounds_range_str(bottom, top):
        if bottom > top or top == 0:
            return '-'
        if bottom == 0:
            return f"{top}"
        if bottom == top:
            return f"{bottom}"
        return f"{bottom}-{top}"

    @property
    def light_wounds(self):
        return self.get_wounds_range_str(self.light_bottom, self.light_top)

    @property
    def medium_wounds(self):
        return self.get_wounds_range_str(self.medium_bottom, self.medium_top)

    @property
    def heavy_wounds(self):
        return self.get_wounds_range_str(self.heavy_bottom, self.heavy_top)
    
    @property
    def deadly_wounds(self):
        return f"{self.deadly_bottom}+"
    

def get_wounds_range_sets() -> namedtuple:
    return [WoundsRangeSet(val) for val in range(1, 51)]


# -----------------------------------------------------------------------------

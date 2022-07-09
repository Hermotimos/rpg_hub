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
        return LoadInfo(load_regular, overload_1, overload_2, overload_3, overload_4)
    
    return [_get_overload_ranges(v) for v in LOAD_LIMITS]


# -----------------------------------------------------------------------------


WOUNDS_RANGES = [
    ['1',   '-',        '-',        '-',        '1+'],
    ['2',   '-',        '-',        '-',        '1+'],
    ['3',   '-',        '-',        '1',        '2+'],
    ['4',   '-',        '1',        '2',        '3+'],
    ['5',   '1',        '2',        '3',        '4+'],
    ['6',   '1',        '2',        '3',        '4+'],
    ['7',   '1 - 2',    '3',        '4',        '5+'],
    ['8',   '1 - 2',    '3',        '4',        '5+'],
    ['9',   '1 - 2',    '3 - 4',    '5',        '6+'],
    ['10',  '1 - 2',    '3 - 4',    '5',        '6+'],
    ['11',  '1 - 2',    '3 - 4',    '5 - 6',    '7+'],
    ['12',  '1 - 2',    '3 - 4',    '5 - 6',    '7+'],
    ['13',  '1 - 3',    '4 - 5',    '6',        '7+'],
    ['14',  '1 - 3',    '4 - 5',    '6',        '7+'],
    ['15',  '1 - 3',    '4 - 5',    '6',        '7+'],
    ['16',  '2 - 3',    '4 - 5',    '6 - 7',    '8+'],
    ['17',  '2 - 3',    '4 - 5',    '6 - 7',    '8+'],
    ['18',  '2 - 3',    '4 - 6',    '7 - 8',    '9+'],
    ['19',  '2 - 3',    '4 - 6',    '7 - 8',    '9+'],
    ['20',  '2 - 4',    '5 - 6',    '7 - 9',    '10+'],
    ['21',  '3 - 4',    '5 - 7',    '8 - 9',    '10+'],
    ['22',  '3 - 4',    '5 - 7',    '8 - 10',   '11+'],
    ['23',  '3 - 5',    '6 - 8',    '9 - 10',   '11+'],
    ['24',  '3 - 5',    '6 - 8',    '9 - 11',   '12+'],
    ['25',  '4 - 5',    '6 - 8',    '9 - 11',   '12+'],
    ['26',  '4 - 5',    '6 - 8',    '9 - 12',   '13+'],
    ['27',  '4 - 5',    '6 - 9',    '10 - 12',  '13+'],
    ['28',  '4 - 6',    '7 - 9',    '10 - 13',  '14+'],
    ['29',  '4 - 6',    '7 - 9',    '10 - 13',  '14+'],
    ['30',  '5 - 6',    '7 - 9',    '10 - 14',  '15+'],
    ['31',  '5 - 6',    '7 - 10',   '11 - 14',  '15+'],
    ['32',  '5 - 6',    '7 - 10',   '11 - 15',  '16+'],
    ['33',  '5 - 7',    '8 - 10',   '11 - 15',  '16+'],
    ['34',  '6 - 7',    '8 - 12',   '13 - 16',  '17+'],
    ['35',  '6 - 8',    '9 - 12',   '13 - 16',  '17+'],
    ['36',  '6 - 8',    '9 - 13',   '14 - 17',  '18+'],
    ['37',  '7 - 8',    '9 - 13',   '14 - 17',  '18+'],
    ['38',  '7 - 8',    '9 - 13',   '14 - 18',  '19+'],
    ['39',  '7 - 9',    '10 - 13',  '14 - 18',  '19+'],
    ['40',  '7 - 9',    '10 - 14',  '15 - 19',  '20+'],
    ['41',  '8 - 9',    '10 - 14',  '15 - 19',  '20+'],
    ['42',  '8 - 9',    '10 - 14',  '15 - 20',  '21+'],
    ['43',  '8 - 9',    '10 - 14',  '15 - 20',  '21+'],
    ['44',  '8 - 10',   '11 - 14',  '15 - 21',  '22+'],
    ['45',  '8 - 10',   '11 - 15',  '16 - 21',  '22+'],
    ['46',  '8 - 10',   '11 - 16',  '17 - 22',  '23+'],
    ['47',  '8 - 10',   '11 - 16',  '17 - 22',  '23+'],
    ['48',  '9 - 10',   '11 - 16',  '17 - 23',  '24+'],
    ['49',  '9 - 10',   '11 - 16',  '17 - 23',  '24+'],
    ['50',  '9 - 10',   '11 - 16',  '17 - 22',  '25+'],
]


def get_wounds_ranges() -> namedtuple:
    WoundsRanges = namedtuple(
        'WoundsRanges', ['health', 'light', 'medium', 'heavy', 'deadly'])
    return [WoundsRanges(*vals) for vals in WOUNDS_RANGES]


# -----------------------------------------------------------------------------


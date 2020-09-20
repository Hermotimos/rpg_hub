# Custom filters; ex. for dict lookup

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def dict_lookup(dict_, index):
    if index in dict_:
        return dict_[index]
    return ''


@register.filter
def get_first_word(text):
    return text.split(' ', 1)[0]


@register.filter
def columns(thelist, n):
    """
    [From: https://stackoverflow.com/questions/11864580/rendering-a-list-as-a-2-column-html-table-in-a-django-template]
    Break a list into ``n`` columns, filling up each column to the maximum equal length possible.
    For example::

        from pprint import pprint
        for i in range(7, 11):
            print '%sx%s:' % (i, 3)
            pprint(columns(range(i), 3), width=20)
        7x3:
        [[0, 3, 6],
         [1, 4],
         [2, 5]]
        8x3:
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5]]
        9x3:
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5, 8]]
        10x3:
        [[0, 4, 8],
         [1, 5, 9],
         [2, 6],
         [3, 7]]

        Note that this filter does not guarantee that `n` columns will be present:
        pprint(columns(range(4), 3), width=10)
        [[0, 2],
         [1, 3]]
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    list_len = len(thelist)
    split = list_len // n
    if list_len % n != 0:
        split += 1
    return [thelist[i::split] for i in range(split)]


@register.filter
def ordered_columns(thelist, n):
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    list_len = len(thelist)
    split = list_len // n
    if list_len % n != 0:
        split += 1
    res = []
    # print(thelist)
    for i in range(split + 1):
        # print('indx', i)
        # print('appended:', thelist[0:split])
        if thelist[0:split]:
            res.append(thelist[0:split])
            thelist = thelist[split:]
            print('thelist:', thelist)
    # print('RES:', res)
    return res


@register.filter
def percentage(value):
    return format(value, "%")


# @register.filter
# def underscore_to_space(text):
#     text = str(text)
#     return text.replace('_', ' ')
#
#
# @register.filter
# def rtrim(data, number_of_digits):
#     data = str(data)
#     return data[:-number_of_digits]
#
#
# @register.filter
# def ltrim(data, number_of_digits):
#     data = str(data)
#     return data[number_of_digits:]

@register.filter
def get_max_skill_level(skill_levels_list):
    levels = [skill_lvl.level for skill_lvl in skill_levels_list]
    return max(levels)


@register.filter
def format_as_html(text):
    text = format_html(text)
    return mark_safe(text)


@register.filter
def add_season_img(text):
    if text:
        text = text.replace('. dnia', '')
        replacements = {
            'Wiosny': '<br><img class="img-season" src="/static/img/seasons_spring.png" alt="Season"><br>',
            'Lata': '<br><img class="img-season" src="/static/img/seasons_summer.png" alt="Season"><br>',
            'Jesieni': '<br><img class="img-season" src="/static/img/seasons_autumn.png" alt="Season"><br>',
            'Zimy': '<br><img class="img-season" src="/static/img/seasons_winter.png" alt="Season"><br>',
        }
        cnt = 0
        previous = ''
        for k, v in replacements.items():
            cnt += 1 if k in text else 0
            text = text.replace(k, v)
            if cnt > 1:
                text = text.replace(previous, '')
                text = text.replace(v, (previous[:-4] + v[4:]))
                break
            previous = v
    return mark_safe(text)


@register.filter
def get_model_name(obj):
    return obj.__class__.__name__


@register.filter
def get_audio_path(obj):
    try:
        if obj.audio:
            return obj.audio.path
        else:
            return get_audio_path(obj.in_location)
    except AttributeError:
        return None

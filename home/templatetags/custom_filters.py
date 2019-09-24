# Custom filters; ex. for dict lookup

from django import template

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


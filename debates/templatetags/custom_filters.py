# Custom filters; ex. for dict lookup

from django import template

register = template.Library()


@register.filter
def dict_lookup(dict_, index):
    if index in dict_:
        return dict_[index]
    return ''

#
# @register.filter
# def underscore_to_space(text):
#     text = str(text)
#     return text.replace('_', ' ')


@register.filter
def get_first_word(text):
    return text.split(' ', 1)[0]


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

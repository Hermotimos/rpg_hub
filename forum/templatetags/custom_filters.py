# Custom filters; ex. for dict lookup

from django import template

register = template.Library()


@register.filter
def dict_lookup(dict_, index):
    if index in dict_:
        return dict_[index]
    return ''

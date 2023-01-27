from typing import List

from django.apps import apps
from django.utils.html import format_html
from django.utils.safestring import SafeString


def get_model_by_date(obj):
    year = str(obj.daydate).split('-')[0]
    for model in apps.get_app_config('_todos').get_models():
        if year in model.__name__:
            return model


def compl_daily(obj):
    model = get_model_by_date(obj)
    
    def value(field_name) -> List[str]:
        return getattr(obj, field_name)
    
    def istrue_cnt() -> int:
        return sum(
            value(f) for f in model.CONDITIONS['TRUE']
        )
    
    def iszero_cnt() -> int:
        return sum(
            value(f) == 0 for f in model.CONDITIONS['ZERO']
        )
    
    def ismin_cnt() -> int:
        return sum(
            value(k) >= v for k, v in
            model.CONDITIONS['MINIMUM'].items()
        )
    
    def isnonempty_cnt() -> int:
        return sum(
            value(f) != "" for f in
            model.CONDITIONS['NONEMPTYSTR']
        )

    def isoneof_cnt() -> int:
        return 1 if sum(1 for f in model.CONDITIONS['ONEOF'] if value(f) != "") > 0 else 0
    
    # # print(obj.daydate)
    # if str(obj.daydate) == '2022-10-01':
    #     print(istrue_cnt(), iszero_cnt(), ismin_cnt(), isnonempty_cnt(), isoneof_cnt())

    try:
        sum_completed = istrue_cnt() + iszero_cnt() + ismin_cnt() + isnonempty_cnt() + isoneof_cnt()
        sum_todo = sum(len(f) for f in model.CONDITIONS.values()) - len(model.CONDITIONS['ONEOF']) + 1
        return int(round(sum_completed / sum_todo * 100, 0))
    except AttributeError:
        return 0
    

def compl_monthly(obj):
    sum_days = sum(compl_daily(day) for day in obj.days.all())
    num_days = len(obj.days.all())
    return int(sum_days / num_days)
    

def format_compl(value) -> SafeString:
    colors = {
        range(0, 26): "#ff0000",
        range(26, 51): "#ffa700",
        range(51, 76): "#2cba00",
        range(76, 100): "#007000",
    }
    
    def get_color(val):
        for val_range, code in colors.items():
            if val in val_range:
                return code
    
    return format_html(f'<b style="color: {get_color(value)}">{value} %</b>')




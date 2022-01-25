from django.contrib import admin
from django.utils.translation import ugettext_lazy


class SkillLevelFilter(admin.SimpleListFilter):
    title = ugettext_lazy('skill__name')
    parameter_name = 'skill__name'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        qs.distinct()
        list_with_duplicates = [(i, i) for i in qs.values_list('skill__name', flat=True).distinct()]
        list_without_duplicates = list(dict.fromkeys(list_with_duplicates))
        return list_without_duplicates

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(skill__name__exact=self.value())


class SynergyLevelFilter(admin.SimpleListFilter):
    title = ugettext_lazy('synergy__name')
    parameter_name = 'synergy__name'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        qs.distinct()
        list_with_duplicates = [(i, i) for i in qs.values_list('synergy__name', flat=True).distinct()]
        list_without_duplicates = list(dict.fromkeys(list_with_duplicates))
        return list_without_duplicates

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(synergy__name__exact=self.value())


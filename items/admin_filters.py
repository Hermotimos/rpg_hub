from django.contrib import admin
from django.utils.translation import gettext_lazy


class CollectionFilter(admin.SimpleListFilter):
    title = gettext_lazy('owner__fullname')
    parameter_name = 'owner__fullname'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        return [
            (i, i) for i in qs.values_list('owner__fullname', flat=True).distinct()
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(owner__fullname__exact=self.value())


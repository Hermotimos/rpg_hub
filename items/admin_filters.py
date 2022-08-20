from django.contrib import admin
from django.utils.translation import gettext_lazy


class OwnerFilter(admin.SimpleListFilter):
    title = gettext_lazy('collection__owner__fullname')
    parameter_name = 'collection__owner__fullname'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        return set(
            (i, i) for i in qs.values_list('collection__owner__fullname', flat=True)
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(collection__owner__fullname__exact=self.value())


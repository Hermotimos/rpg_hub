from django.contrib import admin
from history.models import GeneralLocation, SpecificLocation


class SpecificLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'general_location', 'main_image', 'description']
    list_editable = ['general_location', 'description', 'main_image']
    list_filter = ['general_location']
    search_fields = ['name', 'description']


class SpecificLocationInline(admin.TabularInline):
    model = SpecificLocation
    extra = 0


class GeneralLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'main_image', 'description']
    list_editable = ['description', 'main_image']
    search_fields = ['name', 'description']

    inlines = [SpecificLocationInline]


admin.site.register(GeneralLocation, GeneralLocationAdmin)
admin.site.register(SpecificLocation, SpecificLocationAdmin)

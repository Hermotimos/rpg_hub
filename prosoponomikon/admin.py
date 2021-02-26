from django.contrib import admin
from django.db.models import TextField, CharField
from django.forms import Textarea, TextInput
from django.utils.html import format_html

from prosoponomikon.models import Character, NPCCharacter, PlayerCharacter, CharacterGroup, NameForm, NameContinuum, NameGroup, FamilyName


class NameFormAdmin(admin.ModelAdmin):
    list_display = ['id', 'form', 'type', 'is_ancient', 'name_continuum']
    list_editable = ['form', 'type', 'is_ancient', 'name_continuum']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'name_continuum',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield


class NameFormInline(admin.TabularInline):
    model = NameForm
    extra = 0
    
    
class NameContinuumAdmin(admin.ModelAdmin):
    inlines = [NameFormInline]
    list_display = ['id', 'names_in_continuum', 'description']
    list_editable = ['description']
    
    def names_in_continuum(self, obj):
        return obj.__str__()

    
class NameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    list_editable = ['name', 'description']


class FamilyNameAdmin(admin.ModelAdmin):
    list_display = ['id', 'form']
    list_editable = ['form']
    

class CharacterAdmin(admin.ModelAdmin):
    list_display = ['get_img', 'name', 'family_name', 'cognomen', 'description']
    list_editable = ['name', 'family_name', 'cognomen', 'description']
    search_fields = ['name', 'family_name', 'cognomen', 'description']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 50})},
        CharField: {'widget': TextInput(attrs={'size': 25})},
    }

    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'name',
            'family_name',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield
    
    def get_img(self, obj):
        if obj.profile.image:
            return format_html(
                f'<img src="{obj.profile.image.url}" width="70" height="70">'
            )
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('profile')
        return qs


admin.site.register(NameForm, NameFormAdmin)
admin.site.register(FamilyName, FamilyNameAdmin)
admin.site.register(NameContinuum, NameContinuumAdmin)
admin.site.register(NameGroup, NameGroupAdmin)
admin.site.register(CharacterGroup)
admin.site.register(Character, CharacterAdmin)
admin.site.register(PlayerCharacter, CharacterAdmin)
admin.site.register(NPCCharacter, CharacterAdmin)

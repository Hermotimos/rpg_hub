from django.contrib import admin
from django.db.models import TextField, CharField
from django.forms import Textarea, TextInput
from django.utils.html import format_html

from prosoponomikon.models import Character, NPCCharacter, PlayerCharacter, \
    CharacterGroup, FirstName, NameGroup, FamilyName, AffixGroup, AuxiliaryNameGroup


class FirstNameAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
    }
    list_display = [
        'id', 'form', 'is_ancient', 'info', 'affix_group', 'auxiliary_group']
    list_editable = [
        'form', 'is_ancient', 'info', 'affix_group', 'auxiliary_group']
    ordering = ['form']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'affix_group',
            'auxiliary_group',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield
    
    
class FirstNameInline(admin.TabularInline):
    model = FirstName
    extra = 0
    

class FamilyNameAdmin(admin.ModelAdmin):
    list_display = ['id', 'form']
    list_editable = ['form']
    
    
class NameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


class AffixGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'affix', 'type', 'name_group']
    list_editable = ['affix', 'type', 'name_group']


class AuxiliaryNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'color', 'location', 'social_info']
    list_editable = ['color', 'location', 'social_info']


class CharacterAdmin(admin.ModelAdmin):
    list_display = ['get_img', 'first_name', 'family_name', 'cognomen', 'description']
    list_editable = ['first_name', 'family_name', 'cognomen', 'description']
    search_fields = ['first_name', 'family_name', 'cognomen', 'description']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 50})},
        CharField: {'widget': TextInput(attrs={'size': 25})},
    }

    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'first_name',
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


admin.site.register(NameGroup, NameGroupAdmin)
admin.site.register(AffixGroup, AffixGroupAdmin)
admin.site.register(AuxiliaryNameGroup, AuxiliaryNameGroupAdmin)
admin.site.register(FirstName, FirstNameAdmin)
admin.site.register(FamilyName, FamilyNameAdmin)
admin.site.register(CharacterGroup)
admin.site.register(Character, CharacterAdmin)
admin.site.register(PlayerCharacter, CharacterAdmin)
admin.site.register(NPCCharacter, CharacterAdmin)

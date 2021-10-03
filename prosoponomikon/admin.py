from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import TextField, CharField
from django.forms import Textarea, TextInput
from django.utils.html import format_html

from prosoponomikon.models import Character, NPCCharacter, PlayerCharacter, \
    CharacterGroup, FirstName, NameGroup, FamilyName, AffixGroup, \
    AuxiliaryNameGroup, FamilyNameGroup
from rpg_project.utils import formfield_for_dbfield_cached


class FirstNameAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
        CharField: {'widget': TextInput(attrs={'size': 20})},
    }
    list_display = [
        'id', 'form', 'form_2', 'is_ancient', 'info', 'affix_group',
        'auxiliary_group']
    list_editable = [
        'form', 'form_2', 'is_ancient', 'info', 'affix_group',
        'auxiliary_group']
    list_filter = ['auxiliary_group', 'is_ancient']
    ordering = ['form']
    search_fields = ['form', 'form_2']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'affix_group',
            'auxiliary_group',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    
class FirstNameInline(admin.TabularInline):
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 50})},
    }
    model = FirstName
    extra = 10
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'auxiliary_group',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


class FamilyNameAdminForm(forms.ModelForm):
    class Meta:
        model = FamilyName
        fields = ['form', 'info', 'locations', 'group']
        widgets = {
            'locations': FilteredSelectMultiple(
                'Locations', False, attrs={'style': 'height:400px'}
            ),
        }


class FamilyNameAdmin(admin.ModelAdmin):
    form = FamilyNameAdminForm
    list_display = ['id', 'group', 'form', 'info', 'locs']
    list_editable = ['group', 'form', 'info']
    ordering = ['group', 'form']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'group',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('locations', 'group')
        return qs

    def locs(self, obj):
        return " | ".join([loc.name for loc in obj.locations.all()])


class NameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'type', 'description']
    list_editable = ['title', 'type', 'description']


class FamilyNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


class AffixGroupAdmin(admin.ModelAdmin):
    inlines = [FirstNameInline]
    list_display = ['id', 'affix', 'type', 'name_group']
    list_editable = ['affix', 'type', 'name_group']
    list_filter = ['type']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'name_group',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    

class AuxiliaryNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'color', 'location', 'social_info']
    list_editable = ['color', 'location', 'social_info']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'location',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


class CharacterAdminForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = [
            'profile', 'first_name', 'family_name', 'cognomen', 'description',
            'frequented_locations', 'biography_packets', 'dialogue_packets',
            'known_directly', 'known_indirectly',
        ]
        widgets = {
            'frequented_locations': FilteredSelectMultiple(
                'Frequented_locations', False),
            'biography_packets': FilteredSelectMultiple(
                'Biography_packets', False),
            'dialogue_packets': FilteredSelectMultiple(
                'Dialogue_packets', False),
            'known_directly': FilteredSelectMultiple(
                'Known_directly', False),
            'known_indirectly': FilteredSelectMultiple(
                'Known_indirectly', False),
        }


class CharacterAdmin(admin.ModelAdmin):
    form = CharacterAdminForm
    list_display = [
        'get_img', 'first_name', 'family_name', 'cognomen', 'description']
    list_editable = ['first_name', 'family_name', 'cognomen', 'description']
    search_fields = [
        'first_name__form', 'family_name__form', 'cognomen', 'description']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'first_name',
            'family_name',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    def get_img(self, obj):
        if obj.profile.image:
            return format_html(
                f'<img src="{obj.profile.image.url}" width="70" height="70">'
            )
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('profile', 'first_name', 'family_name')
        return qs


class CharacterGroupAdminForm(forms.ModelForm):
    class Meta:
        model = CharacterGroup
        fields = [
            'name', 'author', 'characters', 'default_knowledge_packets',
            'default_skills']
        widgets = {
            'characters': FilteredSelectMultiple('Characters', False),
            'default_knowledge_packets': FilteredSelectMultiple(
                'Pakiety wiedzy', False),
            'default_skills': FilteredSelectMultiple('Umiejetności', False),
        }


class CharacterGroupAdmin(admin.ModelAdmin):
    form = CharacterGroupAdminForm
    

admin.site.register(NameGroup, NameGroupAdmin)
admin.site.register(AffixGroup, AffixGroupAdmin)
admin.site.register(AuxiliaryNameGroup, AuxiliaryNameGroupAdmin)
admin.site.register(FirstName, FirstNameAdmin)
admin.site.register(FamilyNameGroup, FamilyNameGroupAdmin)
admin.site.register(FamilyName, FamilyNameAdmin)
admin.site.register(CharacterGroup, CharacterGroupAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(PlayerCharacter, CharacterAdmin)
admin.site.register(NPCCharacter, CharacterAdmin)

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.html import format_html

from rpg_project.utils import update_rel_objs, formfield_for_dbfield_cached, formfield_with_cache
from rules.models import EliteProfession, EliteKlass, Klass, Plate, Shield, \
    Weapon, Skill
from users.models import Profile


class ProfileAdminForm(forms.ModelForm):
    warning = """
    <b style="color:red">
        PRZY TWORZENIU NOWEGO PROFILU ZAPIS TEGO POLA JEST NIEMOŻLIWY
        <br><br>
        WYPEŁNIJ JE W DRUGIEJ TURZE !!!
    </b>
    """
    
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Skills', False),
        label=format_html(warning),
    )
    klasses = forms.ModelMultipleChoiceField(
        queryset=Klass.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Klasses', False),
        label=format_html(warning),
    )
    elite_professions = forms.ModelMultipleChoiceField(
        queryset=EliteProfession.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Elite Professions', False),
        label=format_html(warning),
    )
    elite_klasses = forms.ModelMultipleChoiceField(
        queryset=EliteKlass.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Elite Klasses', False),
        label=format_html(warning),
    )
    plates = forms.ModelMultipleChoiceField(
        queryset=Plate.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Plates', False),
        label=format_html(warning),
    )
    shields = forms.ModelMultipleChoiceField(
        queryset=Shield.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Shields', False),
        label=format_html(warning),
    )
    weapons = forms.ModelMultipleChoiceField(
        queryset=Weapon.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Weapons', False),
        label=format_html(warning),
    )

    fields_and_models = {
        'skills': Skill,
        'klasses': Klass,
        'elite_professions': EliteProfession,
        'elite_klasses': EliteKlass,
        'plates': Plate,
        'shields': Shield,
        'weapons': Weapon,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        id_ = self.instance.id
        if id_ is None:
            # If this is "New" form, avoid filling "virtual" field with data
            return
        try:
            for field, Model in self.fields_and_models.items():
                self.__dict__['initial'].update(
                    {field: Model.objects.filter(allowees=id_)})
        except AttributeError:
            pass

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        try:
            for field, Model in self.fields_and_models.items():
                update_rel_objs(instance, Model, self.cleaned_data[field], "allowees")
        except ValueError:
            text = self.cleaned_data['text']
            raise ValueError(
                'Przy tworzeniu nowego pakietu nie da się zapisać lokacji - '
                'podaj je jeszcze raz.\n'
                f'SKOPIUJ TREŚC PACZKI, INACZEJ PRACA BĘDZIE UTRACONA:'
                f'\n\n{text}\n\n'
            )
        return instance


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = [
        'get_img', 'id', 'character_name_copy', 'user', 'status', 'is_alive',
        'is_active', 'is_enchanter', 'image']
    list_editable = ['user', 'status', 'is_alive', 'is_active', 'is_enchanter', 'image']
    list_filter = ['user', 'status', 'is_alive', 'is_active', 'is_enchanter', ]
    search_fields = ['user__username', 'character_name_copy']

    def get_img(self, obj):
        if obj.image:
            return format_html(
                f'<img src="{obj.image.url}" width="70" height="70">')
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')
    
    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     fields = [
    #         'user',
    #     ]
    #     return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        fields = [
            'user',
        ]
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in fields:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield

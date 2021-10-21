from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.html import format_html

from rpg_project.utils import update_rel_objs
from rules.models import EliteProfession, EliteKlass, Klass, Plate, Shield, \
    Weapon, Skill, Synergy
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
    synergies = forms.ModelMultipleChoiceField(
        queryset=Synergy.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Synergies', False),
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
        'synergies': Synergy,
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
                    {field: Model.objects.filter(allowed_profiles=id_)})
        except AttributeError:
            pass

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        try:
            for field, Model in self.fields_and_models.items():
                update_rel_objs(
                    instance, Model, self.cleaned_data[field],
                    "allowed_profiles")
        except ValueError:
            text = self.cleaned_data['text']
            raise ValueError(
                'Przy tworzeniu nowego pakietu nie da się zapisać lokacji - '
                'podaj je jeszcze raz.\n'
                f'SKOPIUJ TREŚC PACZKI, INACZEJ PRACA BĘDZIE UTRACONA:'
                f'\n\n{text}\n\n'
            )
        return instance


class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ['get_img', 'id', 'user', 'status', 'is_alive', 'is_active', 'image']
    list_editable = ['status', 'is_alive', 'is_active', 'image']
    list_filter = ['status', 'is_alive', 'is_active']
    search_fields = ['user__username', 'copied_character_name']

    def get_img(self, obj):
        if obj.image:
            return format_html(
                f'<img src="{obj.image.url}" width="70" height="70">')
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')


admin.site.register(Profile, ProfileAdmin)

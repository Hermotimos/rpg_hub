from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from imaginarion.models import PictureSet
from rules.models import Skill, SkillType, Perk, Modifier
from users.models import Profile


class PerkAdminForm(forms.ModelForm):
    modifiers = forms.ModelMultipleChoiceField(
        queryset=Modifier.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Modifiers', False))
        

class Form1(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(
        queryset=Profile.players.all(),
        required=False,
        widget=FilteredSelectMultiple('Allowed profiles', False))


class SkillAdminForm(Form1):
    types = forms.ModelMultipleChoiceField(
        queryset=SkillType.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Types', False))


class SynergyAdminForm(Form1):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Skills', False))


class SkillOrSynergyAdminForm(forms.ModelForm):
    acquired_by = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Acquired by', False))
    perks = forms.ModelMultipleChoiceField(
        queryset=Perk.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Perks', False))


class SkillLevelAdminForm(SkillOrSynergyAdminForm):
    pass
        

class SynergyLevelAdminForm(SkillOrSynergyAdminForm):
    pass
    

class Form2(Form1):
    picture_sets = forms.ModelMultipleChoiceField(
        queryset=PictureSet.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Picture Sets', False))

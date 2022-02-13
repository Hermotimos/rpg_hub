from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from imaginarion.models import PictureSet
from rules.models import Skill, Perk
from users.models import Profile


class PerkAdminForm(forms.ModelForm):
    """An AdminForm with Meta to provide + (add) feature."""
    
    class Meta:
        model = Perk
        fields = ['name', 'description',
                  # 'modifiers',
                  'conditional_modifiers', 'cost', 'comments']
        widgets = {
            # 'modifiers': FilteredSelectMultiple('Modifiers', False),
            'comments': FilteredSelectMultiple('Comments', False),
            'conditional_modifiers': FilteredSelectMultiple('Conditional Modifiers', False),
        }
        

class Form1(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(
        queryset=Profile.players.all(),
        required=False,
        widget=FilteredSelectMultiple('Allowed profiles', False))


class SkillAdminForm(forms.ModelForm):
    """An AdminForm with Meta to provide + (add) feature."""
    
    class Meta:
        model = Skill
        fields = ['name', 'tested_trait', 'image', 'allowed_profiles', 'group',
                  'types', 'sorting_name']
        widgets = {
            'allowed_profiles': FilteredSelectMultiple('Allowed profiles', False),
            'types': FilteredSelectMultiple('Types', False),
        }


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

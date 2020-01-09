from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.html import format_html

from characters.models import Character
from imaginarion.models import Picture
from rules.models import SkillLevel


class CharacterAdminForm(forms.ModelForm):
    skill_levels_acquired = forms.ModelMultipleChoiceField(queryset=SkillLevel.objects.all(), required=False,
                                                           widget=FilteredSelectMultiple('Skill levels', False))
    pictures = forms.ModelMultipleChoiceField(queryset=Picture.objects.all(), required=False,
                                              widget=FilteredSelectMultiple('Pictures', False))


class CharacterAdmin(admin.ModelAdmin):
    form = CharacterAdminForm
    list_display = ['get_img']

    def get_img(self, obj):
        if obj.profile.image:
            return format_html(f'<img width="40" height="40" src="{obj.profile.image.url}">')
        else:
            return format_html(f'<img width="40" height="40" src="media/profile_pics/profile_default.jpg">')


admin.site.register(Character, CharacterAdmin)

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.html import format_html

from characters.models import Character
from imaginarion.models import Picture
from rules.models import SkillLevel


class CharacterAdminForm(forms.ModelForm):
    skill_levels_acquired = forms.ModelMultipleChoiceField(queryset=SkillLevel.objects.all(),
                                                           widget=FilteredSelectMultiple('Skill levels', False),
                                                           required=False)
    pictures = forms.ModelMultipleChoiceField(queryset=Picture.objects.all(),
                                              widget=FilteredSelectMultiple('Pictures', False),
                                              required=False)


class CharacterAdmin(admin.ModelAdmin):
    list_display = ['get_img']
    form = CharacterAdminForm

    def get_img(self, obj):
        if obj.profile.image:
            return format_html(f'<img width="40" height="40" src="{obj.profile.image.url}">')
        else:
            return format_html(f'<img width="40" height="40" src="media/profile_pics/profile_default.jpg">')


admin.site.register(Character, CharacterAdmin)

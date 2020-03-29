from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.forms.widgets import Textarea, TextInput

from imaginarion.models import Picture
from knowledge.models import KnowledgePacket
from rules.models import Skill


class KnowledgePacketAdminForm(forms.ModelForm):
    pictures = forms.ModelMultipleChoiceField(queryset=Picture.objects.all(),
                                              widget=FilteredSelectMultiple('Pictures', False),
                                              required=False)
    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(),
                                            widget=FilteredSelectMultiple('Skills', False),
                                            required=False)


class KnowledgePacketAdmin(admin.ModelAdmin):
    form = KnowledgePacketAdminForm
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 50})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 150})},
    }
    list_display = ['id', 'title', 'text']
    list_editable = ['title', 'text']
    list_filter = ['skills__name']
    search_fields = ['title', 'text']


admin.site.register(KnowledgePacket, KnowledgePacketAdmin)

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q
from django.db import models
from django.forms.widgets import Textarea, TextInput

from imaginarion.models import Picture
from knowledge.models import KnowledgePacket, KnowledgePacketType
from users.models import Profile


class KnowledgePacketAdminForm(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                                      .exclude(Q(character_status='dead_player') |
                                                               Q(character_status='dead_npc') |
                                                               # Q(character_status='gm') |
                                                               Q(character_status='living_npc')),
                                                      widget=FilteredSelectMultiple('Allowed profiles', False),
                                                      required=False)
    pictures = forms.ModelMultipleChoiceField(queryset=Picture.objects.all(),
                                              widget=FilteredSelectMultiple('Pictures', False),
                                              required=False)


class KnowledgePacketAdmin(admin.ModelAdmin):
    form = KnowledgePacketAdminForm
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 50})},
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 100})},
    }
    list_display = ['id', 'title', 'text']
    list_editable = ['title', 'text']
    search_fields = ['title', 'text']


admin.site.register(KnowledgePacket, KnowledgePacketAdmin)
admin.site.register(KnowledgePacketType)

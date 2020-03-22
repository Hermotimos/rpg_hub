from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.db.models import Q
from django.forms import Textarea

from toponomikon.models import GeneralLocation, SpecificLocation, LocationType
from imaginarion.models import Picture
from knowledge.models import KnowledgePacket
from users.models import Profile


class ToponomikonKnownForm(forms.ModelForm):
    known_directly = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                                    .exclude(Q(status='dead_player') |
                                                             Q(status='dead_npc') |
                                                             Q(status='gm') |
                                                             Q(status='living_npc')),
                                                    widget=FilteredSelectMultiple('Known directly', False),
                                                    required=False)
    known_indirectly = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                                      .exclude(Q(status='dead_player') |
                                                               Q(status='dead_npc') |
                                                               Q(status='gm') |
                                                               Q(status='living_npc')),
                                                      widget=FilteredSelectMultiple('Known indirectly', False),
                                                      required=False)
    knowledge_packets = forms.ModelMultipleChoiceField(queryset=KnowledgePacket.objects.all(),
                                                       widget=FilteredSelectMultiple('Knowledge packets', False),
                                                       required=False)
    pictures = forms.ModelMultipleChoiceField(queryset=Picture.objects.all(),
                                              widget=FilteredSelectMultiple('Pictures', False),
                                              required=False)


class SpecificLocationAdmin(admin.ModelAdmin):
    form = ToponomikonKnownForm
    list_display = ['name', 'location_type', 'general_location', 'description']
    list_editable = ['location_type', 'general_location', 'description']
    list_filter = ['general_location__name']
    search_fields = ['name', 'description']


class SpecificLocationInline(admin.TabularInline):
    model = SpecificLocation
    extra = 0

    form = ToponomikonKnownForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 25})},
    }


class GeneralLocationAdmin(admin.ModelAdmin):
    form = ToponomikonKnownForm
    inlines = [SpecificLocationInline]
    list_display = ['name', 'location_type', 'description', 'main_image']
    list_editable = ['location_type', 'description', 'main_image']
    search_fields = ['name', 'description']


class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_img']
    list_editable = ['default_img']


admin.site.register(LocationType, LocationTypeAdmin)
admin.site.register(GeneralLocation, GeneralLocationAdmin)
admin.site.register(SpecificLocation, SpecificLocationAdmin)

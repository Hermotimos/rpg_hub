from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.db.models import Q
from django.forms.widgets import TextInput
from django.utils.html import format_html

from imaginarion.models import Picture
from knowledge.models import KnowledgePacket
from rules.models import Skill
from toponomikon.models import Location


class KnowledgePacketAdminForm(forms.ModelForm):
    pictures = forms.ModelMultipleChoiceField(
        queryset=Picture.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Pictures', False),
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Skills', False),
    )
    gen_locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(in_location=None),
        required=False,
        widget=FilteredSelectMultiple('General locations', False),
        label=format_html('<b style="color:red">'
                          'PRZY TWORZENIU NOWEJ ZAPIS LOKACJI JEST NIEMOŻLIWY'
                          '<br><br>'
                          'PODAJ LOKACJĘ W DRUGIEJ TURZE :)'
                          '</b>'),
    )
    spec_locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(~Q(in_location=None)),
        required=False,
        widget=FilteredSelectMultiple('Specific locations', False),
        label=format_html('<b style="color:red">'
                          'PRZY TWORZENIU NOWEJ ZAPIS LOKACJI JEST NIEMOŻLIWY'
                          '<br><br>'
                          'PODAJ LOKACJĘ W DRUGIEJ TURZE :)'
                          '</b>'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        id_ = self.instance.id
        if id_ is None:
            # trick to avoid new forms being populated with previous data
            # I don't understand why that happens, but this works...
            # TODO research this
            return
        try:
            gen_locs = Location.objects.filter(in_location=None).filter(knowledge_packets=id_)
            self.__dict__['initial'].update({'gen_locations': gen_locs})
        except AttributeError:
            pass
        try:
            spec_locs = Location.objects.filter(~Q(in_location=None)).filter(knowledge_packets=id_)
            self.__dict__['initial'].update({'spec_locations': spec_locs})
        except AttributeError:
            pass

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        gen_loc_ids = self.cleaned_data['gen_locations']
        spec_loc_ids = self.cleaned_data['spec_locations']
        try:
            for gen_loc in Location.objects.filter(in_location=None).filter(id__in=gen_loc_ids):
                gen_loc.knowledge_packets.add(instance)
                gen_loc.save()
            for spec_loc in Location.objects.filter(~Q(in_location=None)).filter(id__in=spec_loc_ids):
                spec_loc.knowledge_packets.add(instance)
                spec_loc.save()
        except ValueError:
            text = self.cleaned_data['text']
            raise ValueError(
                'Przy tworzeniu nowej paczki nie da się zapisać lokacji - '
                'podaj je jeszcze raz.\n'
                f'SKOPIUJ TREŚC PACZKI, INACZEJ PRACA BĘDZIE UTRACONA:'
                f'\n\n{text}\n\n'
            )
        return instance


class KnowledgePacketAdmin(admin.ModelAdmin):
    form = KnowledgePacketAdminForm
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 50})},
    }
    list_display = ['id', 'title', 'text', 'get_acquired_by']
    list_editable = ['title', 'text']
    list_filter = ['skills__name']
    search_fields = ['title', 'text']
    
    def get_acquired_by(self, obj):
        img_urls = [profile.image.url for profile in obj.acquired_by.all()]
        html = ''
        if img_urls:
            for url in img_urls:
                html += f'<img width="40" height="40" src="{url}">&nbsp;'
        else:
            html = '<h1><font color="red">NIKT</font></h1>'
        return format_html(html)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('acquired_by')
        return qs


admin.site.register(KnowledgePacket, KnowledgePacketAdmin)


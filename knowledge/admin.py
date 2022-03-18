from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q, CharField, TextField
from django.forms.widgets import TextInput, Textarea
from django.utils.html import format_html

from knowledge.models import KnowledgePacket, MapPacket, BiographyPacket, \
    DialoguePacket
from rpg_project.utils import update_rel_objs
from toponomikon.models import Location, PrimaryLocation, SecondaryLocation


@admin.register(DialoguePacket)
class DialoguePacketAdmin(admin.ModelAdmin):
    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': 50})},
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 100})},
    }
    list_display = ['id', 'title', 'text']
    list_editable = ['title', 'text']
    search_fields = ['title']


class BiographyPacketAdminForm(forms.ModelForm):
    class Meta:
        model = BiographyPacket
        fields = [
            'title', 'text', 'author', 'acquired_by', 'picture_sets', 'order_no']
        widgets = {
            'acquired_by': FilteredSelectMultiple('Acquired by', False),
            'picture_sets': FilteredSelectMultiple('Picture Sets', False),
        }


@admin.register(BiographyPacket)
class BiographyPacketAdmin(admin.ModelAdmin):
    form = BiographyPacketAdminForm
    list_display = ['id', 'title', 'text', 'author']
    list_editable = ['title', 'text']
    search_fields = ['title', 'text']
    list_select_related = ['author']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('acquired_by__user', 'picture_sets__pictures')
        return qs


class KnowledgePacketAdminForm(forms.ModelForm):
    
    class Meta:
        model = KnowledgePacket
        fields = [
            'title', 'text', 'author', 'acquired_by', 'skills', 'picture_sets']
        widgets = {
            'acquired_by': FilteredSelectMultiple('Acquired by', False),
            'skills': FilteredSelectMultiple('Skills', False),
            'picture_sets': FilteredSelectMultiple('Picture Sets', False),
        }
    
    warning = """
    <b style="color:red">
        PRZY TWORZENIU NOWEGO PAKIETU ZAPIS LOKACJI JEST NIEMOŻLIWY
        <br><br>
        PODAJ LOKACJĘ W DRUGIEJ TURZE :)
    </b>
    """
    primary_locs = forms.ModelMultipleChoiceField(
        queryset=PrimaryLocation.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Primary locations', False),
        label=format_html(warning),
    )
    secondary_locs = forms.ModelMultipleChoiceField(
        queryset=SecondaryLocation.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Secondary locations', False),
        label=format_html(warning),
    )
    
    fields_and_models = {
        'primary_locs': PrimaryLocation,
        'secondary_locs': SecondaryLocation,
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
                    {field: Model.objects.filter(knowledge_packets=id_)})
        except AttributeError:
            pass

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        try:
            for field, Model in self.fields_and_models.items():
                update_rel_objs(
                    instance, Model, self.cleaned_data[field],
                    "knowledge_packets")
        except ValueError:
            text = self.cleaned_data['text']
            raise ValueError(
                'Przy tworzeniu nowego pakietu nie da się zapisać lokacji - '
                'podaj je jeszcze raz.\n'
                f'SKOPIUJ TREŚC PACZKI, INACZEJ PRACA BĘDZIE UTRACONA:'
                f'\n\n{text}\n\n'
            )
        return instance
    

@admin.register(KnowledgePacket)
class KnowledgePacketAdmin(admin.ModelAdmin):
    form = KnowledgePacketAdminForm
    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': 50})},
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
    
        
class MapPacketAdminForm(forms.ModelForm):
    
    class Meta:
        model = MapPacket
        fields = ['picture_sets']
        widgets = {
            'picture_sets': FilteredSelectMultiple('Picture Sets', False),
        }

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
            gen_locs = Location.objects.filter(in_location=None).filter(map_packets=id_)
            self.__dict__['initial'].update({'gen_locations': gen_locs})
        except AttributeError:
            pass
        try:
            spec_locs = Location.objects.filter(~Q(in_location=None)).filter(map_packets=id_)
            self.__dict__['initial'].update({'spec_locations': spec_locs})
        except AttributeError:
            pass

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        gen_loc_ids = self.cleaned_data['gen_locations']
        spec_loc_ids = self.cleaned_data['spec_locations']
        try:
            for gen_loc in Location.objects.filter(in_location=None).filter(id__in=gen_loc_ids):
                gen_loc.map_packets.add(instance)
                gen_loc.save()
            for spec_loc in Location.objects.filter(~Q(in_location=None)).filter(id__in=spec_loc_ids):
                spec_loc.map_packets.add(instance)
                spec_loc.save()
        except ValueError:
            raise ValueError('Przy tworzeniu nowej paczki nie da się zapisać '
                             'lokacji - podaj jeszcze raz !!!\n')
        return instance


@admin.register(MapPacket)
class MapPacketAdmin(admin.ModelAdmin):
    form = MapPacketAdminForm
    list_display = ['id', 'title', 'get_acquired_by']
    list_editable = ['title']
    search_fields = ['title']
    
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
        qs = qs.prefetch_related('acquired_by', 'picture_sets')
        return qs

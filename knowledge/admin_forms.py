from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q
from django.utils.html import format_html

from knowledge.models import KnowledgePacket, MapPacket, DialoguePacket
from prosoponomikon.models import Character
from rpg_project.utils import update_rel_objs
from toponomikon.models import Location, PrimaryLocation, SecondaryLocation


WARNING = """
    <b style="color:red">
        PRZY TWORZENIU NOWEGO PAKIETU ZAPIS TEGO POLA JEST NIEMOŻLIWY<br><br>
        WYPEŁNIJ W DRUGIEJ TURZE :)
    </b>
"""


class DialoguePacketAdminForm(forms.ModelForm):
    
    class Meta:
        model = DialoguePacket
        fields = ['title', 'text']
    
    characters = forms.ModelMultipleChoiceField(
        queryset=Character.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Characters', False),
        label=format_html(WARNING),
    )
    
    fields_and_models = {
        'characters': Character,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        id_ = self.instance.id
        if id_ is None:
            # If this is "New" form, avoid filling "virtual" field with data
            return
        try:
            for field, Model in self.fields_and_models.items():
                self.__dict__['initial'].update({field: Model.objects.filter(dialogue_packets=id_)})
        except AttributeError:
            pass
    
    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        try:
            for field, Model in self.fields_and_models.items():
                update_rel_objs(instance, Model, self.cleaned_data[field], "dialogue_packets")
        except ValueError:
            text = self.cleaned_data['text']
            raise ValueError(
                'Przy tworzeniu nowego pakietu nie da się zapisać Postaci - '
                'podaj je jeszcze raz.\n'
                'SKOPIUJ TREŚC PAKIETU, INACZEJ PRACA BĘDZIE UTRACONA:'
                f'\n\n{text}\n\n'
            )
        return instance
    

# -----------------------------------------------------------------------------


class KnowledgePacketAdminForm(forms.ModelForm):
    
    class Meta:
        model = KnowledgePacket
        fields = [
            'author', 'title', 'text', 'references', 'acquired_by', 'skills',
            'picture_sets'
        ]
    
    primary_locs = forms.ModelMultipleChoiceField(
        queryset=PrimaryLocation.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Primary locations', False),
        label=format_html(WARNING),
    )
    secondary_locs = forms.ModelMultipleChoiceField(
        queryset=SecondaryLocation.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Secondary locations', False),
        label=format_html(WARNING),
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
                self.__dict__['initial'].update({field: Model.objects.filter(knowledge_packets=id_)})
        except AttributeError:
            pass

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        try:
            for field, Model in self.fields_and_models.items():
                update_rel_objs(instance, Model, self.cleaned_data[field], "knowledge_packets")
        except ValueError:
            text = self.cleaned_data['text']
            raise ValueError(
                'Przy tworzeniu nowego pakietu nie da się zapisać lokacji - '
                'podaj je jeszcze raz.\n'
                f'SKOPIUJ TREŚC PAKIETU, INACZEJ PRACA BĘDZIE UTRACONA:'
                f'\n\n{text}\n\n'
            )
        return instance
    
        
# -----------------------------------------------------------------------------


class MapPacketAdminForm(forms.ModelForm):
    
    class Meta:
        model = MapPacket
        fields = ['title', 'acquired_by', 'picture_sets']

    primary_locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(in_location=None),
        required=False,
        widget=FilteredSelectMultiple('Primary locations', False),
        label=format_html(WARNING),
    )
    secondary_locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(~Q(in_location=None)),
        required=False,
        widget=FilteredSelectMultiple('Secondary locations', False),
        label=format_html(WARNING),
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
            self.__dict__['initial'].update({'primary_locations': gen_locs})
        except AttributeError:
            pass
        try:
            spec_locs = Location.objects.filter(~Q(in_location=None)).filter(map_packets=id_)
            self.__dict__['initial'].update({'secondary_locations': spec_locs})
        except AttributeError:
            pass

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        gen_loc_ids = self.cleaned_data['primary_locations']
        spec_loc_ids = self.cleaned_data['secondary_locations']
        try:
            for gen_loc in Location.objects.filter(in_location=None).filter(id__in=gen_loc_ids):
                gen_loc.map_packets.add(instance)
                gen_loc.save()
            for spec_loc in Location.objects.filter(~Q(in_location=None)).filter(id__in=spec_loc_ids):
                spec_loc.map_packets.add(instance)
                spec_loc.save()
        except ValueError:
            raise ValueError('Przy tworzeniu nowej paczki nie da się zapisać lokacji - podaj jeszcze raz !!!\n')
        return instance

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import (
    CharField,
    FileField,
    ModelForm,
    ModelMultipleChoiceField,
)
from django.forms.widgets import SelectMultiple

from knowledge.models import KnowledgePacket, BiographyPacket
from toponomikon.models import Location


class KnPacketForm(ModelForm):
    """Form to create KnowledgePackets by 'gm' status profiles."""
    locations = ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label='Lokacje powiązane',
    )

    class Meta:
        model = KnowledgePacket
        fields = ['title', 'text', 'skills', 'picture_sets']
        widgets = {
            'picture_sets': SelectMultiple(attrs={'size': 15}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        instance = kwargs.pop('instance')
        if instance:
            self.fields['locations'].initial = Location.objects.filter(
                knowledge_packets=instance)

        self.fields['text'].label = "Tekst"
        self.fields['title'].label = "Tytuł"
        self.fields['skills'].label = "Umiejętności powiązane"

        self.fields['locations'].widget.attrs['size'] = 10
        self.fields['skills'].widget.attrs['size'] = 10
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
        }
        
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz pakiet wiedzy', css_class='btn-dark'))


class PlayerKnPacketForm(KnPacketForm):
    """Form to create KnowledgePackets by 'player' status profiles."""
    
    class Meta:
        model = KnowledgePacket
        exclude = ['acquired_by', 'picture_sets', 'author']
    
    picture_1 = FileField(required=False, label='')
    descr_1 = CharField(required=False, label='')
    
    picture_2 = FileField(required=False, label='')
    descr_2 = CharField(required=False, label='')
    
    picture_3 = FileField(required=False, label='')
    descr_3 = CharField(required=False, label='')

    def __init__(self, *args, **kwargs):
        current_profile = kwargs.pop('current_profile')
        super().__init__(*args, **kwargs)
        
        self.fields['text'].label = "Tekst"
        self.fields['title'].label = "Tytuł"

        self.fields['locations'].queryset = (
                current_profile.locations_participated.all()
                | current_profile.locations_informed.all()
        ).distinct()
        self.fields['skills'].queryset = current_profile.allowed_skills.all()

        self.fields['descr_1'].widget.attrs = {
            'placeholder': 'Podpis grafiki nr 1',
        }
        self.fields['descr_2'].widget.attrs = {
            'placeholder': 'Podpis grafiki nr 2',
        }
        self.fields['descr_3'].widget.attrs = {
            'placeholder': 'Podpis grafiki nr 3',
        }


class BioPacketForm(ModelForm):
    """Form to create BiographyPackets by 'gm' status profiles."""
    
    class Meta:
        model = BiographyPacket
        fields = ['title', 'text', 'picture_sets', 'order_no']
        widgets = {
            'picture_sets': SelectMultiple(attrs={'size': 15}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['order_no'].label = """
            Nr porządkowy (równe numery są sortowane alfabetycznie)"""
        
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
        }
        
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz pakiet biograficzny', css_class='btn-dark'))


class PlayerBioPacketForm(BioPacketForm):
    """Form to create BiographyPackets by 'player' status profiles."""
    
    class Meta:
        model = BiographyPacket
        exclude = ['acquired_by', 'picture_sets', 'sorting_name', 'author']
    
    picture_1 = FileField(required=False, label='')
    descr_1 = CharField(required=False, label='')
    
    picture_2 = FileField(required=False, label='')
    descr_2 = CharField(required=False, label='')
    
    picture_3 = FileField(required=False, label='')
    descr_3 = CharField(required=False, label='')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['descr_1'].widget.attrs = {
            'placeholder': 'Podpis grafiki nr 1',
        }
        self.fields['descr_2'].widget.attrs = {
            'placeholder': 'Podpis grafiki nr 2',
        }
        self.fields['descr_3'].widget.attrs = {
            'placeholder': 'Podpis grafiki nr 3',
        }

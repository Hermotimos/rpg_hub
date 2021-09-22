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
        label='Lokacje powiązane (niewymagane)',
    )

    class Meta:
        model = KnowledgePacket
        fields = ['title', 'text', 'skills', 'picture_sets']
        widgets = {
            'pictures': SelectMultiple(attrs={'size': 15}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['locations'].widget.attrs['size'] = 10
        self.fields['skills'].widget.attrs['size'] = 10
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
        }
        instance = kwargs.pop('instance')
        if instance:
            self.fields['locations'].initial = Location.objects.filter(
                knowledge_packets=instance)
            
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz pakiet wiedzy', css_class='btn-dark'))


class PlayerKnPacketForm(KnPacketForm):
    """Form to create KnowledgePackets by 'player' status profiles."""
    
    class Meta:
        model = KnowledgePacket
        exclude = ['acquired_by', 'sorting_name', 'author']
    
    picture_1 = FileField(required=False, label='')
    descr_1 = CharField(required=False, label='')
    
    picture_2 = FileField(required=False, label='')
    descr_2 = CharField(required=False, label='')
    
    picture_3 = FileField(required=False, label='')
    descr_3 = CharField(required=False, label='')

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
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
        self.fields['locations'].queryset = (
                profile.locs_known_directly.all()
                | profile.locs_known_indirectly.all()
        ).distinct()
        self.fields['skills'].queryset = profile.allowed_skills.all()


class BioPacketForm(ModelForm):
    """Form to create BiographyPackets by 'gm' status profiles."""
    
    class Meta:
        model = BiographyPacket
        fields = ['title', 'text', 'pictures', 'order_no']
        widgets = {
            'pictures': SelectMultiple(attrs={'size': 15}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_no'].label = "Nr porządkowy (równe numery są " \
                                        "sortowane alfabetycznie)"
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
        exclude = ['acquired_by', 'pictures', 'sorting_name', 'author']
    
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

from django.forms import (
    CharField,
    FileField,
    ModelForm,
    ModelMultipleChoiceField,
)
from django.forms.widgets import SelectMultiple

from knowledge.models import KnowledgePacket
from toponomikon.models import Location


class KnPacketCreateForm(ModelForm):
    """Form to create KnowledgePackets by 'gm' status profiles."""
    class Meta:
        model = KnowledgePacket
        fields = ['title', 'text', 'skills', 'pictures']
        widgets = {
            'pictures': SelectMultiple(attrs={'size': 15}),
        }
        
    locations = ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['locations'].label = 'Połącz z lokacjami (opcjonalnie):'
        self.fields['locations'].widget.attrs['size'] = 10
        self.fields['skills'].label = 'Połącz z umiejętnościami:'
        self.fields['skills'].widget.attrs['size'] = 10
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Treść pakietu wiedzy*',
        }
        self.fields['title'].label = ''
        self.fields['title'].widget.attrs = {
            'placeholder': 'Tytuł pakietu wiedzy (max. 100 znaków)*',
        }


class PlayerKnPacketCreateForm(KnPacketCreateForm):
    """Form to create KnowledgePackets by 'player' status profiles."""
    class Meta:
        model = KnowledgePacket
        exclude = ['acquired_by', 'pictures', 'sorting_name', 'author']
    
    picture_1 = FileField(required=False, label='')
    picture_2 = FileField(required=False, label='')
    picture_3 = FileField(required=False, label='')
    description_1 = CharField(required=False, label='')
    description_2 = CharField(required=False, label='')
    description_3 = CharField(required=False, label='')

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        super().__init__(*args, **kwargs)
        self.fields['description_1'].widget.attrs = {
            'placeholder': 'Podpis grafiki nr 1',
        }
        self.fields['description_2'].widget.attrs = {
            'placeholder': 'Podpis grafiki nr 2',
        }
        self.fields['description_3'].widget.attrs = {
            'placeholder': 'Podpis grafiki nr 3',
        }
        self.fields['locations'].queryset = (
                profile.locs_known_directly.all()
                | profile.locs_known_indirectly.all()
        ).distinct()
        self.fields['skills'].queryset = profile.allowed_skills.all()

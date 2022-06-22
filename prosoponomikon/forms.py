from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from prosoponomikon.models import Character, FirstName


class CharacterForm(forms.ModelForm):
    """Form used in 'users' app to fill in Character details."""
    
    class Meta:
        model = Character
        fields = ['description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].label = "OPIS POSTACI"
        self.fields['description'].widget.attrs[
            'placeholder'
        ] = "Krótka charakterystyka - jak Postać jawi się nowo poznanym osobom"


class CharacterCreateForm(forms.ModelForm):
    
    class Meta:
        model = Character
        fields = [
            'first_name', 'family_name', 'cognomen', 'description',
            'frequented_locations', 'acquaintances',
        ]

    NAME_TYPES = (
        ('MALE', 'MALE'),
        ('FEMALE', 'FEMALE'),
        ('DAEMON', 'DAEMON'),
    )
    username = forms.CharField(max_length=250)
    is_alive = forms.BooleanField(required=False, initial=True)
    image = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        custom_order = [
            'username', 'first_name', 'family_name', 'cognomen', 'is_alive',
            'image', 'description', 'frequented_locations', 'acquaintances',
        ]
        self.fields = {
            f_name: self.fields[f_name] for f_name in custom_order
        }
        self.fields['first_name'].queryset = FirstName.objects.order_by('form')
        self.fields['frequented_locations'].widget.attrs['size'] = 12
        self.fields['acquaintances'].widget.attrs['size'] = 10
    
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz Postać', css_class='btn-dark'))

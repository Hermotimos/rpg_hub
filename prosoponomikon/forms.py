from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from prosoponomikon.models import Character, FirstName, Acquaintanceship


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
    is_alive = forms.BooleanField(required=False, initial=True)
    image = forms.ImageField()

    class Meta:
        model = Character
        fields = [
            'first_name', 'family_name', 'cognomen', 'description',
            'frequented_locations',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        custom_order = [
            'first_name', 'family_name', 'cognomen', 'is_alive',
            'image', 'description', 'frequented_locations',
        ]
        self.fields = {f_name: self.fields[f_name] for f_name in custom_order}
        self.fields['first_name'].queryset = FirstName.objects.order_by('form')
        self.fields['frequented_locations'].widget.attrs['size'] = 12
    
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz Postać', css_class='btn-dark'))


class ForPlayerAcquaintanceshipCreateForm(forms.ModelForm):
    is_alive = forms.BooleanField(required=False, initial=True)
    is_direct = forms.BooleanField(required=False, initial=False)
    
    class Meta:
        model = Character
        fields = ['cognomen', 'description', 'frequented_locations']
    
    def __init__(self, *args, **kwargs):
        current_profile = kwargs.pop('current_profile')
        super().__init__(*args, **kwargs)
        
        custom_order = [
            'cognomen', 'description', 'is_alive', 'is_direct',
            'frequented_locations',
        ]
        self.fields = {f_name: self.fields[f_name] for f_name in custom_order}

        self.fields['frequented_locations'].help_text = """
            ✧ Aby zaznaczyć wiele Lokacji - użyj CTRL albo SHIFT.<br>
        """
        if self.instance:
            acquaintanceship = Acquaintanceship.objects.get(
                known_character=self.instance,
                knowing_character=current_profile.character)
            self.fields['is_alive'].initial = self.instance.profile.is_alive
            self.fields['is_direct'].initial = acquaintanceship.is_direct

        self.fields['cognomen'].label = "Imię"
        self.fields['description'].label = "Opis"
        self.fields['is_alive'].label = "Czy Postać jest żywa?"
        self.fields['is_direct'].label = "Czy Postać jest znana osobiście?"
        self.fields['frequented_locations'].label = "Lokacje"
        
        self.fields['frequented_locations'].queryset = current_profile.locations_known_annotated()
        self.fields['frequented_locations'].widget.attrs['size'] = 12
        
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz Postać', css_class='btn-dark'))

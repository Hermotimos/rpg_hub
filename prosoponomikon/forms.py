from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Field, Submit
from django import forms

from prosoponomikon.models import CharacterGroup, Character, FirstName

CharacterManyGroupsEditFormSet = forms.modelformset_factory(
    model=CharacterGroup,
    fields=[
        'name', 'order_no', 'characters', 'default_knowledge_packets',
        'default_skills'
    ],
    extra=0,
    can_delete=True,
)


class CharacterGroupsEditFormSetHelper(FormHelper):
    def __init__(self, status=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(Submit('submit', 'Zapisz zmiany', css_class='btn-dark'))
        self.form_show_labels = False
        self.layout = Layout(
            Row(
                Column(
                    PrependedText('order_no', '',
                                  placeholder="Nr porządkowy (równe numery "
                                              "są sortowane alfabetycznie)"),
                    css_class='form-group col-sm-3 mb-0'
                ),
                Column(
                    PrependedText('name', '', placeholder="Nazwa nowej grupy"),
                    css_class='form-group col-sm-8 mb-0'),
                Column('DELETE', css_class='form-group col-sm-1 mb-0', title="Usunąć grupę?"),
            ),
            Row(
                Column(Div(), css_class='col-sm-3 mb-0'),
                Column(Field('characters', size=15), css_class='form-group col-sm-9 mb-0'),
            ),
        )
        if status == 'gm':
            self.layout.fields.append(
                Row(
                    Column(Div(), css_class='col-sm-3 mb-0'),
                    Column(Field('default_knowledge_packets', size=15), css_class='form-group col-sm-9 mb-0'),
                ),
            )
            self.layout.fields.append(
                Row(
                    Column(Div(), css_class='col-sm-3 mb-0'),
                    Column(Field('default_skills', size=10), css_class='form-group col-sm-9 mb-0'),
                ),
            )


class CharacterGroupCreateForm(forms.ModelForm):
    
    class Meta:
        model = CharacterGroup
        fields = [
            'name',
            'characters',
            'order_no',
            'default_knowledge_packets',
            'default_skills',
        ]

    def __init__(self, profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['characters'].label = "Postacie"
        self.fields['default_knowledge_packets'].label = """
            Domyślne pakiety wiedzy NPC w grupie
        """
        self.fields['default_skills'].label = """
            Domyślne umiejętności NPC w grupie
        """
        self.fields['name'].label = "Nazwa nowej grupy"
        self.fields['order_no'].label = """
            Nr porządkowy (równe numery są sortowane alfabetycznie)
        """
        
        if profile.status != 'gm':
            self.fields['characters'].queryset = \
                profile.characters_all_known_annotated_if_indirectly()
            self.fields['default_knowledge_packets'].widget = forms.HiddenInput()
            self.fields['default_skills'].widget = forms.HiddenInput()
            
        self.fields['characters'].widget.attrs['size'] = 15
        self.fields['default_knowledge_packets'].widget.attrs['size'] = 15
        self.fields['default_skills'].widget.attrs['size'] = 15

        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz grupę Postaci', css_class='btn-dark'))


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
        """'name' and 'family_name' can only be chosen from the existing ones.
        # Creating new instances of name and family_name requires info about
        # their locations and other modalities. Hence it's restricted to admin.
        """
        model = Character
        fields = ['first_name', 'family_name', 'cognomen', 'description',
                  'frequented_locations', 'known_directly', 'known_indirectly']

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
            'image', 'description', 'frequented_locations', 'known_directly',
            'known_indirectly',
        ]
        self.fields = {
            f_name: self.fields[f_name] for f_name in custom_order
        }
        self.fields['first_name'].queryset = FirstName.objects.order_by('form')
        self.fields['frequented_locations'].widget.attrs['size'] = 12
        self.fields['known_directly'].widget.attrs['size'] = 10
        self.fields['known_indirectly'].widget.attrs['size'] = 10
    
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz Postać', css_class='btn-dark'))

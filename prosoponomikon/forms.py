from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Field
from crispy_forms.layout import Submit
from django.forms import modelformset_factory, ModelForm, HiddenInput

from prosoponomikon.models import CharacterGroup, Character

CharacterManyGroupsEditFormSet = modelformset_factory(
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


class CharacterGroupCreateForm(ModelForm):
    
    class Meta:
        model = CharacterGroup
        fields = [
            'name',
            'characters',
            'order_no',
            'default_knowledge_packets',
            'default_skills',
        ]

    def __init__(self, status=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Nazwa nowej grupy"
        self.fields['order_no'].label = "Nr porządkowy (równe numery " \
                                        "są sortowane alfabetycznie)"
        self.fields['characters'].widget.attrs['size'] = 15
        self.fields['default_knowledge_packets'].widget.attrs['size'] = 15
        self.fields['default_skills'].widget.attrs['size'] = 15

        if status != 'gm':
            self.fields['default_knowledge_packets'].widget = HiddenInput()
            self.fields['default_skills'].widget = HiddenInput()
            
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz grupę postaci', css_class='btn-dark'))


class CharacterForm(ModelForm):
    """Form used in 'users' app to fill in Character details."""
    
    class Meta:
        model = Character
        fields = ['description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].label = "OPIS POSTACI"
        self.fields['description'].widget.attrs[
            'placeholder'
        ] = "Krótka charakterystyka - jak postać jawi się nowo poznanym osobom"

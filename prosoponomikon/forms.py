from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Field
from crispy_forms.layout import Submit
from django.forms import modelformset_factory, ModelForm, HiddenInput

from prosoponomikon.models import CharacterGroup, Character


CharacterManyGroupsEditFormSet = modelformset_factory(
    model=CharacterGroup,
    fields=['name', 'order_no', 'characters', 'default_knowledge_packets'],
    extra=1,
    can_delete=True,
)
CharacterSingleGroupEditFormSet = modelformset_factory(
    model=CharacterGroup,
    fields=['name', 'order_no', 'characters', 'default_knowledge_packets'],
    extra=0,
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


class CharacterForm(ModelForm):
    """Form used in 'users' app to fill in Character details."""
    
    class Meta:
        model = Character
        fields = ['family_name', 'cognomen', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].label = "OPIS POSTACI"
        self.fields['description'].widget.attrs[
            'placeholder'
        ] = "Krótka charakterystyka - jak postać jawi się nowo poznanym osobom"
        
        warning = " (Po zatwierdzeniu edycja jedynie przez MG)"
        self.fields['family_name'].label = "NAZWISKO" + warning
        self.fields['family_name'].widget.attrs['size'] = 10
        self.fields['cognomen'].label = "PRZYDOMEK (np. 'z Astinary')" + warning
        
        if self.instance.family_name:
            self.fields['family_name'].widget = HiddenInput()
        if self.instance.cognomen:
            self.fields['cognomen'].widget = HiddenInput()
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Div
from crispy_forms.layout import Submit
from django.forms import ModelForm, modelformset_factory

from prosoponomikon.models import CharacterGroup


class CharacterGroupCreateForm(ModelForm):
    """Form to create CharacterGroup's for Players."""
    
    class Meta:
        model = CharacterGroup
        exclude = ['author', 'default_knowledge_packets']
        help_texts = {
            'characters': """
                Aby zaznaczyć wiele postaci - użyj CTRL albo SHIFT.<br>
                Postać może należeć do dowolnej liczby grup.
            """,
        }
       
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['characters'].widget.attrs['size'] = 10
        # TODO filter queryset as per user's known characters (make such method on profile/user)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Utwórz grupę', css_class='btn-dark'))


class GMCharcterGroupCreateForm(CharacterGroupCreateForm):
    """Form to create CharacterGroup's for Game Masters."""
    
    class Meta:
        model = CharacterGroup
        exclude = ['author']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['default_knowledge_packets'].widget.attrs['size'] = 10


CharacterGroupsOrderFormSet = modelformset_factory(
    model=CharacterGroup,
    fields=['name', 'order_no', 'characters'],
    extra=1,
    can_delete=True,
)


class CharacterGroupsOrderFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(Submit('submit', 'Zapisz zmiany', css_class='btn-dark'))
        self.form_show_labels = False
        self.layout = Layout(
            Row(
                Column(
                    PrependedText('order_no', '', placeholder="Nr porządkowy"),
                    css_class='form-group col-sm-3 mb-0'
                ),
                Column(
                    PrependedText('name', '', placeholder="Nazwa nowej grupy"),
                    css_class='form-group col-sm-8 mb-0'),
                Column('DELETE', css_class='form-group col-sm-1 mb-0', title="Usunąć grupę?"),
            ),
            Row(
                Column(Div(), css_class='col-sm-3 mb-0'),
                Column('characters', css_class='form-group col-sm-9 mb-0'),
            ),
        )


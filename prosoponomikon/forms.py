from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm

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
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Utwórz grupę', css_class='btn-dark'))


class GMCharacterGroupCreateForm(CharacterGroupCreateForm):
    """Form to create CharacterGroup's for Game Masters."""
    
    class Meta:
        model = CharacterGroup
        exclude = ['author']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['default_knowledge_packets'].widget.attrs['size'] = 10

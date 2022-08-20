from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Submit, Div
from django.forms import modelformset_factory, Textarea
from django.forms.models import BaseModelFormSet

from items.models import Item


class BaseItemFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        character = kwargs.pop('character')
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['collection'].choices = [('', '--------')] + [(x.pk, x.name) for x in character.collections.all()]
            
            
ItemFormSet = modelformset_factory(
    Item,
    # TODO is_deleted flag
    extra=4,
    fields=('name', 'info', 'weight', 'collection', 'is_deleted'),
    formset=BaseItemFormSet,
    widgets={
        "info": Textarea(attrs={'rows': 1}),
    },
)


class ItemFormSetHelper(FormHelper):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.add_input(Submit('submit', 'Zapisz', css_class='btn-dark d-block mx-auto mt-2'))
        self.form_show_labels = False
        self.layout = Layout(
            Row(
                Div('collection', css_class='col-sm-2 m-0 p-0 pl-1', title="Typ"),
                Div('name', css_class='col-sm-5 m-0 p-0 pl-1', title="Przedmiot"),
                Div('weight', css_class='col-sm-1 m-0 p-0 pl-1', title="Waga"),
                Div('info', css_class='col-sm-3 m-0 p-0 pl-1', title="Opis"),
                Div('is_deleted', css_class='col-sm-1 m-0 p-0', title="Usunąć?"),
                css_class='item-formset',
            ))

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field, Div
from django.forms import modelformset_factory, Textarea

from items.models import Item


ItemFormSet = modelformset_factory(
    Item,
    can_delete=True,
    can_delete_extra=False,
    extra=4,
    fields=('name', 'info', 'weight', 'type', 'collection'),
    widgets={
        "info": Textarea(attrs={'rows': 1}),
    },
)


class ItemFormSetHelper(FormHelper):
    pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_input(Submit('submit', 'Zapisz', css_class='btn-dark d-block mx-auto mt-2'))
        self.form_show_labels = False
        self.layout = Layout(
            Row(
                Div('collection', css_class='col-sm-2 m-0 p-0 pl-1', title="Typ"),
                Div('name', css_class='col-sm-5 m-0 p-0 pl-1', title="Przedmiot"),
                Div('weight', css_class='col-sm-1 m-0 p-0 pl-1', title="Waga"),
                Div('info', css_class='col-sm-3 m-0 p-0 pl-1', title="Info"),
                Div('DELETE', css_class='col-sm-1 m-0 p-0', title="Usunąć?"),
                css_class='item-formset'
            ))

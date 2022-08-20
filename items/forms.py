from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django.forms import modelformset_factory, Textarea

from items.models import Item


ItemFormSet = modelformset_factory(
    Item,
    can_delete=True,
    can_delete_extra=False,
    extra=4,
    fields=('name', 'info', 'weight', 'type'),
    widgets={
        "info": Textarea(attrs={'rows': 1}),
    },
)


class ItemFormSetHelper(FormHelper):
    pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_input(Submit('submit', 'Zapisz', css_class='btn-dark d-block mx-auto'))
        self.form_show_labels = False
        self.layout = Layout(
            Row(
                Column('type', css_class='col-sm-2 m-0 p-0 pl-1', title="Typ"),
                Column('name', css_class='col-sm-4 m-0 p-0 pl-1', title="Przedmiot"),
                Column('weight', css_class='col-sm-2 m-0 p-0 pl-1', title="Waga"),
                Column('info', css_class='col-sm-3 m-0 p-0 pl-1', title="Info"),
                Column('DELETE', css_class='col-sm-1 m-0 p-0', title="Usunąć?"),
            ))

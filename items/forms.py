from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django.forms import modelformset_factory, Textarea
from django.forms.widgets import HiddenInput

from items.models import Item


ItemFormSet = modelformset_factory(
    Item,
    fields=('name', 'info', 'weight', 'collection'),
    can_delete=True,
    widgets={
        "collection": HiddenInput,
        "info": Textarea(attrs={'rows': 1}),
    }
)

# TODO can_delete_extra  Default: True
#  While setting can_delete=True, specifying can_delete_extra=False will remove the option to delete extra forms.

print(ItemFormSet.form.__dict__)


class ItemFormSetHelper(FormHelper):
    pass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_input(Submit('submit', 'Zapisz', css_class='btn-dark d-block mx-auto'))
        self.form_show_labels = False
        self.layout = Layout(
            Row(
                Column('name', css_class='col-sm-5 m-0 p-0 pl-1', title="Przedmiot"),
                Column('weight', css_class='col-sm-2 m-0 p-0 pl-1', title="Waga"),
                Column('info', css_class='col-sm-4 m-0 p-0 pl-1', title="Info"),
                Column('DELETE', css_class='col-sm-1 m-0 p-0', title="Usunąć?"),
                Column('collection', type="hidden"),
            ))

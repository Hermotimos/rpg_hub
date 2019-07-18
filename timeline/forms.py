from django import forms
from timeline.models import Event


class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(CreateEventForm, self).__init__(*args, **kwargs)
        self.fields['threads'].widget.attrs = {'size': 10}
        self.fields['description'].widget.attrs = {'cols': 50, 'rows': 5}
        self.fields['participants'].widget.attrs = {'size': 8}
        self.fields['informed'].widget.attrs = {'size': 8}
        self.fields['specific_locations'].widget.attrs = {'size': 10}


class EventAddInformedForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['informed']

    def __init__(self, *args, **kwargs):
        super(EventAddInformedForm, self).__init__(*args, **kwargs)
        self.fields['informed'].label = ''

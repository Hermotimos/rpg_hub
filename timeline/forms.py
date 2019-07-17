from django import forms
from timeline.models import Event


class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ()


class EventAddInformedForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['informed']

    def __init__(self, *args, **kwargs):
        super(EventAddInformedForm, self).__init__(*args, **kwargs)
        self.fields['informed'].label = ''

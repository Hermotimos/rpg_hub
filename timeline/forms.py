from django import forms
from pagedown.widgets import PagedownWidget
from timeline.models import Event, EventNote


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


class EditEventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(EditEventForm, self).__init__(*args, **kwargs)
        self.fields['threads'].widget.attrs = {'size': 10}
        self.fields['description'].widget.attrs = {'cols': 50, 'rows': 5}
        self.fields['participants'].widget.attrs = {'size': 8}
        self.fields['informed'].widget.attrs = {'size': 8}
        self.fields['specific_locations'].widget.attrs = {'size': 10}


class EventNoteForm(forms.ModelForm):
    class Meta:
        model = EventNote
        fields = [
            'text',
            'color'
        ]

    text = forms.CharField(
        label='',
        required=False,
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twoja notatka (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )

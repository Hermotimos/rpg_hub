from django import forms
from django.db.models import Q
from history.models import TimelineEvent, TimelineEventNote, ChronicleEvent, ChronicleEventNote, Thread
from users.models import Profile


# ------ ChronicleEvent model -----


class ChronicleEventCreateForm(forms.ModelForm):
    class Meta:
        model = ChronicleEvent
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {'cols': 60, 'rows': 10}
        self.fields['informed'].widget.attrs = {'size': 10}
        self.fields['participants'].widget.attrs = {'size': 10}
        self.fields['pictures'].widget.attrs = {'size': 10}


class ChronicleEventEditForm(forms.ModelForm):
    class Meta:
        model = ChronicleEvent
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {'cols': 60, 'rows': 10}
        self.fields['informed'].widget.attrs = {'size': 10}
        self.fields['participants'].widget.attrs = {'size': 10}
        self.fields['pictures'].widget.attrs = {'size': 10}


class ChronicleEventNoteForm(forms.ModelForm):
    class Meta:
        model = ChronicleEventNote
        fields = [
            'text',
            'color'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].label = 'Kolor tekstu'
        self.fields['text'].label = ''
        self.fields['text'].required = False
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Twoje przemyślenia (max. 4000 znaków)*',
        }


# ------ TimelineEvent model ------


class TimelineEventCreateForm(forms.ModelForm):
    class Meta:
        model = TimelineEvent
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {'cols': 60, 'rows': 10}
        self.fields['informed'].widget.attrs = {'size': 10}
        self.fields['participants'].widget.attrs = {'size': 10}
        self.fields['specific_locations'].widget.attrs = {'size': 10}
        self.fields['threads'].queryset = Thread.objects.exclude(is_ended=True)
        self.fields['threads'].widget.attrs = {'size': 10}


class TimelineEventEditForm(forms.ModelForm):
    class Meta:
        model = TimelineEvent
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {'cols': 60, 'rows': 10}
        self.fields['informed'].widget.attrs = {'size': 10}
        self.fields['participants'].widget.attrs = {'size': 10}
        self.fields['general_locations'].widget.attrs = {'size': 10}
        self.fields['specific_locations'].widget.attrs = {'size': 10}
        self.fields['threads'].widget.attrs = {'size': 10}


class TimelineEventNoteForm(forms.ModelForm):
    class Meta:
        model = TimelineEventNote
        fields = [
            'text',
            'color'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].label = 'Kolor tekstu'
        self.fields['text'].label = ''
        self.fields['text'].required = False
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Twoje przemyślenia (max. 4000 znaków)*',
        }

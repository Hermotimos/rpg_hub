from django import forms
from history.models import TimelineEvent, ChronicleEvent, Thread


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

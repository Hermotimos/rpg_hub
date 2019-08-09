from django import forms
from django.db.models import Q
from pagedown.widgets import PagedownWidget
from history.models import TimelineEvent, TimelineEventNote, ChronicleEvent, ChronicleEventNote
from users.models import Profile


# ------ TimelineEvent model ------


class TimelineEventCreateForm(forms.ModelForm):
    class Meta:
        model = TimelineEvent
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(TimelineEventCreateForm, self).__init__(*args, **kwargs)
        self.fields['threads'].widget.attrs = {'size': 10}
        self.fields['description'].widget.attrs = {'cols': 50, 'rows': 5}
        self.fields['participants'].widget.attrs = {'size': 8}
        self.fields['informed'].widget.attrs = {'size': 8}
        self.fields['specific_locations'].widget.attrs = {'size': 10}


class TimelineEventInformForm(forms.ModelForm):
    class Meta:
        model = TimelineEvent
        fields = ['informed']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        old_informed_ids = kwargs.pop('old_informed_ids')
        participants_ids = kwargs.pop('participants_ids')
        the_knowing_ids = participants_ids + old_informed_ids
        super(TimelineEventInformForm, self).__init__(*args, **kwargs)
        uninformable_profiles = Profile.objects.exclude(Q(user=authenticated_user) |
                                                        Q(character_status='dead_player') |
                                                        Q(character_status='dead_npc') |
                                                        Q(character_status='living_npc') |
                                                        Q(character_status='gm'))
        self.fields['informed'].queryset = uninformable_profiles.exclude(id__in=the_knowing_ids)
        self.fields['informed'].label = ''


class TimelineEventEditForm(forms.ModelForm):
    class Meta:
        model = TimelineEvent
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(TimelineEventEditForm, self).__init__(*args, **kwargs)
        self.fields['threads'].widget.attrs = {'size': 10}
        self.fields['description'].widget.attrs = {'cols': 60, 'rows': 10}
        self.fields['participants'].widget.attrs = {'size': 8}
        self.fields['informed'].widget.attrs = {'size': 8}
        self.fields['specific_locations'].widget.attrs = {'size': 10}


class TimelineEventNoteForm(forms.ModelForm):
    class Meta:
        model = TimelineEventNote
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

    def __init__(self, *args, **kwargs):
        super(TimelineEventNoteForm, self).__init__(*args, **kwargs)
        self.fields['color'].label = 'Kolor'


# ------ ChronicleEvent model -----


class ChronicleEventCreateForm(forms.ModelForm):
    class Meta:
        model = ChronicleEvent
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(ChronicleEventCreateForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {'cols': 50, 'rows': 5}
        self.fields['participants'].widget.attrs = {'size': 8}
        self.fields['informed'].widget.attrs = {'size': 8}


class ChronicleEventEditForm(forms.ModelForm):
    class Meta:
        model = ChronicleEvent
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(ChronicleEventEditForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {'cols': 60, 'rows': 10}
        self.fields['participants'].widget.attrs = {'size': 8}
        self.fields['informed'].widget.attrs = {'size': 8}


class ChronicleEventInformForm(forms.ModelForm):
    class Meta:
        model = ChronicleEvent
        fields = ['informed']

    def __init__(self, *args, **kwargs):
        super(ChronicleEventInformForm, self).__init__(*args, **kwargs)
        self.fields['informed'].label = ''


class ChronicleEventNoteForm(forms.ModelForm):
    class Meta:
        model = ChronicleEventNote
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

    def __init__(self, *args, **kwargs):
        super(ChronicleEventNoteForm, self).__init__(*args, **kwargs)
        self.fields['color'].label = 'Kolor'

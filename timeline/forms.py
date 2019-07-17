from django import forms
from timeline.models import Event


class CreateOrEditEvent(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'year',
            'season',
            'day_start',
            'day_end',
            'threads',
            'description',
            'participants',
            'informed',
            'general_location',
            'specific_locations',
            'game_no'
        ]

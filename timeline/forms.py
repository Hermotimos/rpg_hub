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
            'thread',
            'description',
            'participants',
            'informed',
            'location1',
            'location2',
            'game_no'
        ]


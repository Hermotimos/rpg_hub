from django import forms

from .models import News


class CreateNewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            'title',
            'text',
            'allowed_users'
        ]

    title = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Tytuł ogłoszenia',
                'size': '60'
            }
        )
    )

    text = forms.CharField(
        label='',
        max_length=4000,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Twoje ogłoszenie',
                'rows': 10,
                'cols': 60
            }
        )
    )

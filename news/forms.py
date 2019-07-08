from django import forms
from news.models import News
from pagedown.widgets import PagedownWidget


class CreateNewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            'title',
            'text',
            'allowed_profiles',
            'image'
        ]

    title = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': f'Tytuł ogłoszenia (max. 100 znaków)',
                'size': '60'
            }
        )
    )

    text = forms.CharField(
        label='',
        max_length=4000,
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twoje ogłoszenie (max. 4000 znaków)',
                'rows': 10,
                'cols': 60
            }
        )
    )

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )
# TODO why image doesn't affect actual form ?? no label, required=False could be absent...
from django import forms
from pagedown.widgets import PagedownWidget
from contact.models import Demand


class ReportForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['text']

    text = forms.CharField(
        label='',
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twoje zgłoszenie (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['response']

    response = forms.CharField(
        label='',
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twoja odpowiedź (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )
from django import forms
from pagedown.widgets import PagedownWidget
from contact.models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['text']

    text = forms.CharField(
        label='',
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Opisz problem (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )

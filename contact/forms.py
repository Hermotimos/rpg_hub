from django import forms
from django.db.models import Q
from pagedown.widgets import PagedownWidget
from contact.models import Demand, DemandAnswer
from users.models import User


class DemandForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['addressee', 'text', 'image']

    addressee = forms.ModelChoiceField(
        label='',
        queryset=User.objects.filter(
            Q(profile__character_status='active_player') |
            Q(profile__character_status='inactive_player') |
            Q(profile__character_status='gm')
        )
    )

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

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )


class DemandTodoForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['text', 'image']

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

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )


class DemandModifyForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['text', 'image']

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

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )


class DemandAnswerForm(forms.ModelForm):
    class Meta:
        model = DemandAnswer
        fields = ['text', 'image']

    text = forms.CharField(
        label='',
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twoja odpowiedź (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )

from django import forms
from django.db.models import Q
from pagedown.widgets import PagedownWidget
from contact.models import Demand, DemandAnswer
from users.models import User


class DemandsCreateForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['addressee', 'text', 'image']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super(DemandsCreateForm, self).__init__(*args, **kwargs)
        self.fields['addressee'].label = 'Adresat:'
        self.fields['addressee'].queryset = User.objects.exclude(Q(id=authenticated_user.id) |
                                                                 Q(profile__character_status='dead_player') |
                                                                 Q(profile__character_status='inactive_player') |
                                                                 Q(profile__character_status='dead_npc') |
                                                                 Q(profile__character_status='living_npc'))

    text = forms.CharField(
        label='',
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twój dezyderat (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )


class PlansCreateForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['text', 'image']

    text = forms.CharField(
        label='',
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twój plan... (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )


class DemandsModifyForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['text', 'image']

    text = forms.CharField(
        label='',
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Treść (max. 4000 znaków)*',
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
                'placeholder': 'Odpowiedź (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )

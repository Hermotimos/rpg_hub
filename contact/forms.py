from django import forms
from django.db.models import Q
from contact.models import Demand, DemandAnswer, Plan
from users.models import User


# ------------------- DEMANDS -------------------


class DemandsCreateForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['addressee', 'image', 'text']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        self.fields['addressee'].label = 'Adresat:'
        self.fields['addressee'].queryset = User.objects.exclude(Q(id=authenticated_user.id) |
                                                                 Q(profile__character_status='dead_player') |
                                                                 Q(profile__character_status='inactive_player') |
                                                                 Q(profile__character_status='dead_npc') |
                                                                 Q(profile__character_status='living_npc')
                                                                 ).order_by('username')
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Odpowiedź (max. 4000 znaków)*'
        }


class DemandAnswerForm(forms.ModelForm):
    class Meta:
        model = DemandAnswer
        fields = ['text', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Odpowiedź (max. 4000 znaków)*'
        }


# ------------------- PLANS -------------------


class PlansCreateForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['inform_gm', 'text', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inform_gm'].label = 'Poinformuj MG'
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 15,
            'placeholder': 'Twój plan... (max. 4000 znaków)*'
        }


class PlansModifyForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['inform_gm', 'text', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inform_gm'].label = 'Poinformuj MG'
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Treść (max. 4000 znaków)*'
        }

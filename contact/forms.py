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
        super(DemandsCreateForm, self).__init__(*args, **kwargs)
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
        self.fields['text'].widget.attrs['placeholder'] = 'Twój dezyderat (max. 4000 znaków)*'
        self.fields['text'].widget.attrs['rows'] = 10
        self.fields['text'].widget.attrs['cols'] = 60


class DemandsModifyForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['text', 'image']

    def __init__(self, *args, **kwargs):
        super(DemandsModifyForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs['placeholder'] = 'Treść (max. 4000 znaków)*'
        self.fields['text'].widget.attrs['rows'] = 10
        self.fields['text'].widget.attrs['cols'] = 60


class DemandAnswerForm(forms.ModelForm):
    class Meta:
        model = DemandAnswer
        fields = ['text', 'image']

    def __init__(self, *args, **kwargs):
        super(DemandAnswerForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs['placeholder'] = 'Odpowiedź (max. 4000 znaków)*'
        self.fields['text'].widget.attrs['rows'] = 10
        self.fields['text'].widget.attrs['cols'] = 60


# ------------------- PLANS -------------------


class PlansCreateForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['inform_gm', 'text', 'image']

    def __init__(self, *args, **kwargs):
        super(PlansCreateForm, self).__init__(*args, **kwargs)
        self.fields['inform_gm'].label = 'Poinformuj MG'
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs['placeholder'] = 'Twój plan... (max. 4000 znaków)*'
        self.fields['text'].widget.attrs['rows'] = 15
        self.fields['text'].widget.attrs['cols'] = 60


class PlansModifyForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['inform_gm', 'text', 'image']

    def __init__(self, *args, **kwargs):
        super(PlansModifyForm, self).__init__(*args, **kwargs)
        self.fields['inform_gm'].label = 'Poinformuj MG'
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs['placeholder'] = 'Treść (max. 4000 znaków)*'
        self.fields['text'].widget.attrs['rows'] = 10
        self.fields['text'].widget.attrs['cols'] = 60

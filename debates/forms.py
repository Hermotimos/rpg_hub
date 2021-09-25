from django import forms
from django.forms.widgets import HiddenInput
from django.db.models import Q

from debates.models import Remark, Debate, Topic
from users.models import Profile


class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CreateDebateForm(forms.ModelForm):
    class Meta:
        model = Debate
        fields = ['title', 'known_directly', 'is_exclusive']
        help_texts = {
            'known_directly': """
                ***Aby zaznaczyć wiele postaci - użyj CTRL albo SHIFT.<br><br>
                1) Włączaj tylko postacie znajdujące się w pobliżu w chwili
                    zakończenia ostatniej sesji.<br>
                2) Postacie w pobliżu niewłączone do narady mogą to zauważyć.<br>
                3) Jeśli chcesz zaczekać na sposobny moment, powiadom MG.<br>
                4) Jeśli na liście brakuje postaci, powiadom MG.<br><br>
            """,
            'is_exclusive': 'Wykluczyć możliwość dodawania uczestników?',
        }

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        if authenticated_user.profile.status != 'gm':
            self.fields['is_exclusive'].widget = HiddenInput()
        if authenticated_user.profile.status == 'gm':
            self.fields['known_directly'].queryset = Profile.living.all()
        else:
            self.fields['known_directly'].queryset = Profile.living.filter(
                character__in=authenticated_user.profile.characters_known_directly.all()
            ).exclude(user=authenticated_user).select_related()
        self.fields['known_directly'].widget.attrs['size'] = 10


class CreateRemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = ['author', 'text', 'image']

    def __init__(self, *args, **kwargs):
        debate_id = kwargs.pop('debate_id', None)
        if debate_id:
            debate = Debate.objects.get(id=debate_id)
            debate_known_directly = debate.known_directly.all()
        else:
            debate_known_directly = Profile.living.all()
            
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        if authenticated_user.profile.status != 'gm':
            self.fields['author'].widget = HiddenInput()
        else:
            self.fields['author'].queryset = Profile.objects.filter(
                Q(status='gm') | Q(id__in=debate_known_directly)
            )
            
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
        }

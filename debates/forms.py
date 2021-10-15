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

        self.fields['title'].label = "Tytuł nowego tematu"


class CreateDebateForm(forms.ModelForm):
    
    class Meta:
        model = Debate
        fields = ['topic', 'title', 'known_directly', 'is_exclusive']
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
        profile = authenticated_user.profile
        super().__init__(*args, **kwargs)
        
        topic = Topic.objects.all()
        known_directly = Profile.living.all()
        
        if profile.status != 'gm':
            self.fields['is_exclusive'].widget = HiddenInput()
            
            topic = Topic.objects.filter(
                debates__known_directly=profile).distinct()
            
            known_directly = known_directly.filter(
                character__in=profile.characters_known_directly.all()
            ).exclude(user=authenticated_user).select_related()
            
        self.fields['topic'].queryset = topic
        self.fields['known_directly'].queryset = known_directly
        
        self.fields['is_exclusive'].label = "Narada zamknięta?"
        self.fields['known_directly'].label = "Uczestnicy"
        self.fields['title'].label = "Tytuł"
        self.fields['topic'].label = "Temat"
        
        self.fields['known_directly'].widget.attrs['size'] = min(
            len(known_directly), 10)


class CreateRemarkForm(forms.ModelForm):
    
    class Meta:
        model = Remark
        fields = ['author', 'text', 'image']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        known_directly = kwargs.pop('known_directly')
        super().__init__(*args, **kwargs)
        
        if authenticated_user.profile.status != 'gm':
            self.fields['author'].widget = HiddenInput()
        else:
            self.fields['author'].queryset = Profile.objects.filter(
                Q(status='gm') | Q(id__in=known_directly)
            )
        
        self.fields['author'].label = "Autor"
        self.fields['image'].label = "Obraz"
        self.fields['text'].label = ''

        self.fields['text'].widget.attrs = {
            'cols': 60, 'rows': 10,
            'placeholder': 'Twoja wypowiedź (max. 4000 znaków)*'
        }

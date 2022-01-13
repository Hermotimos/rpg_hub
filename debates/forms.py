from django import forms
from django.forms.widgets import HiddenInput
from django.db.models import Q

# from debates.models import Remark, Debate, Topic
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
                ***Aby zaznaczyć wiele Postaci - użyj CTRL albo SHIFT.<br><br>
                1) Włączaj tylko Postacie znajdujące się w pobliżu w chwili
                    zakończenia ostatniej sesji.<br>
                2) Postacie w pobliżu niewłączone do narady mogą to zauważyć.<br>
                3) Jeśli chcesz zaczekać na sposobny moment, powiadom MG.<br>
                4) Jeśli na liście brakuje Postaci, powiadom MG.<br><br>
            """,
            'is_exclusive': 'Wykluczyć możliwość dodawania uczestników?',
        }

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        super().__init__(*args, **kwargs)

        self.fields['is_exclusive'].label = "Narada zamknięta?"
        self.fields['known_directly'].label = "Uczestnicy"
        self.fields['title'].label = "Tytuł"
        self.fields['topic'].label = "Temat"

        topic_qs = Topic.objects.all()
        known_directly = Profile.living.all()
        
        if profile.status != 'gm':
            self.fields['is_exclusive'].widget = HiddenInput()
            
            topic_id = kwargs['initial']['topic'].id \
                if kwargs['initial']['topic'] else None
            topic_qs = topic_qs.filter(
                Q(debates__known_directly=profile) | Q(id=topic_id)
            ).distinct()
            
            known_directly = known_directly.filter(
                character__in=profile.characters_known_directly.all()
            ).exclude(id=profile.id).select_related()
            
        self.fields['topic'].queryset = topic_qs
        self.fields['known_directly'].queryset = known_directly
        
        self.fields['known_directly'].widget.attrs['size'] = min(
            len(known_directly), 10)


class CreateRemarkForm(forms.ModelForm):
    
    class Meta:
        model = Remark
        fields = ['author', 'text', 'image']

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        known_directly = kwargs.pop('known_directly')
        super().__init__(*args, **kwargs)

        self.fields['author'].label = "Autor"
        self.fields['image'].label = "Załącz obraz"
        self.fields['text'].label = ''

        if profile.status != 'gm':
            self.fields['author'].widget = HiddenInput()
        else:
            self.fields['author'].queryset = Profile.objects.filter(
                Q(status='gm') | Q(id__in=known_directly)
            )

        self.fields['text'].widget.attrs = {
            'cols': 60, 'rows': 10,
            'placeholder': 'Twoja wypowiedź (max. 4000 znaków)*'
        }

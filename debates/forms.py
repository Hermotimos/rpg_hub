from django import forms
from django.db.models import Q

from debates.models import Remark, Debate, Topic
from users.models import Profile
from users.models import User


class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = ''
        self.fields['title'].max_length = 50
        self.fields['title'].widget.attrs = {
            'size': 60,
            'placeholder': 'Nowy temat narad (max. 50 znaków)*'
        }


class CreateDebateForm(forms.ModelForm):
    class Meta:
        model = Debate
        fields = ['known_directly', 'is_individual', 'name']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        self.fields['known_directly'].label = ''
        self.fields['known_directly'].queryset = Profile.objects.exclude(Q(user=authenticated_user) |
                                                                           Q(status='dead_player') |
                                                                           Q(status='dead_npc') |
                                                                           Q(status='gm'))
        self.fields['known_directly'].widget.attrs['size'] = 10
        self.fields['is_individual'].label = 'Dyskusja indywidualna?'
        self.fields['name'].label = ''
        self.fields['name'].max_length = 100
        self.fields['name'].widget.attrs = {'placeholder': 'Tytuł nowej narady (max. 100 znaków)*'}


class CreateRemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = ['author', 'text', 'image']

    def __init__(self, *args, **kwargs):
        debate_id = kwargs.pop('debate_id')
        if debate_id:
            debate = Debate.objects.get(id=debate_id)
            debate_known_directly = debate.known_directly.all()
        else:
            debate_known_directly = Profile.objects.exclude(Q(status='dead_player') |
                                                              Q(status='dead_npc'))
        super().__init__(*args, **kwargs)
        self.fields['author'].label = 'Autor:'
        self.fields['author'].queryset = User.objects\
            .filter(Q(profile__status='gm') | Q(profile__in=debate_known_directly))\
            .order_by('profile__character_name')
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Twój głos w naradzie (max. 4000 znaków)*'
        }

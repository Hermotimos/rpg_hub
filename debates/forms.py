from django import forms
from debates.models import Remark, Debate, Topic
from users.models import Profile
from django.db.models import Q
from pagedown.widgets import PagedownWidget
from users.models import User


class CreateRemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = [
            'author',
            'text',
            'image'
        ]

    author = forms.ModelChoiceField(
        label='Autor:',
        queryset=User.objects.all(),
    )

    text = forms.CharField(
        label='',
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twój głos w naradzie (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )


class CreateDebateForm(forms.ModelForm):
    class Meta:
        model = Debate
        fields = [
            'allowed_profiles',
            'is_individual',
            'title',
        ]

    title = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Tytuł nowej narady (max. 100 znaków)*',
            }
        )
    )

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super(CreateDebateForm, self).__init__(*args, **kwargs)
        self.fields['allowed_profiles'].queryset = Profile.objects.exclude(Q(user=authenticated_user) |
                                                                           Q(character_status='dead_player') |
                                                                           Q(character_status='dead_npc') |
                                                                           Q(character_status='gm'))
        self.fields['allowed_profiles'].label = ''
        self.fields['allowed_profiles'].widget.attrs['size'] = 10
        self.fields['is_individual'].label = 'Dyskusja indywidualna?'


class UpdateDebateForm(forms.ModelForm):
    class Meta:
        model = Debate
        fields = ['allowed_profiles']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        already_allowed_profiles_ids = kwargs.pop('already_allowed_profiles_ids')
        super(UpdateDebateForm, self).__init__(*args, **kwargs)
        unallowable_profiles = Profile.objects.exclude(Q(user=authenticated_user) |
                                                                           Q(character_status='dead_player') |
                                                                           Q(character_status='dead_npc') |
                                                                           Q(character_status='gm'))
        self.fields['allowed_profiles'].queryset = unallowable_profiles.exclude(id__in=already_allowed_profiles_ids)
        self.fields['allowed_profiles'].label = ''


class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = [
            'title',
            'description'
        ]

    title = forms.CharField(
        max_length=50,
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nowy temat narad (max. 50 znaków)*',
                'size': '60'
            }
        )
    )

    description = forms.CharField(
        max_length=100,
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Opis  (max. 100 znaków)',
                'size': '60',
            }
        )
    )

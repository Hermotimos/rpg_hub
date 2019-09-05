from django import forms
from news.models import News, NewsAnswer
from users.models import Profile
from django.db.models import Q
from pagedown.widgets import PagedownWidget


class CreateNewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            'allowed_profiles',
            'image',
            'text',
            'title',
        ]

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )

    text = forms.CharField(
        label='',
        max_length=4000,
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twoje ogłoszenie (max. 4000 znaków)*',
                'rows': 10,
                'cols': 60
            }
        )
    )

    title = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Tytuł ogłoszenia (max. 100 znaków)*',
                'size': '60'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super(CreateNewsForm, self).__init__(*args, **kwargs)
        self.fields['allowed_profiles'].queryset = Profile.objects.exclude(Q(user=authenticated_user) |
                                                                           Q(character_status='dead_player') |
                                                                           Q(character_status='inactive_player') |
                                                                           Q(character_status='living_npc') |
                                                                           Q(character_status='dead_npc') |
                                                                           Q(character_status='gm'))
        self.fields['allowed_profiles'].label = ''


class CreateNewsAnswerForm(forms.ModelForm):
    class Meta:
        model = NewsAnswer
        fields = [
            'text',
            'image'
        ]

    text = forms.CharField(
        label='',
        max_length=4000,
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

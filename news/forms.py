from django import forms
from news.models import News, NewsAnswer
from users.models import Profile
from django.db.models import Q


class CreateNewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            'allowed_profiles',
            'image',
            'text',
            'title',
        ]

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super(CreateNewsForm, self).__init__(*args, **kwargs)
        self.fields['allowed_profiles'].label = ''
        self.fields['allowed_profiles'].queryset = Profile.objects.exclude(Q(user=authenticated_user) |
                                                                           Q(character_status='dead_player') |
                                                                           Q(character_status='inactive_player') |
                                                                           Q(character_status='living_npc') |
                                                                           Q(character_status='dead_npc') |
                                                                           Q(character_status='gm'))
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].max_length = 4000
        self.fields['text'].widget.attrs['placeholder'] = 'Twoje ogłoszenie (max. 4000 znaków)*'
        self.fields['text'].widget.attrs['rows'] = 10
        self.fields['text'].widget.attrs['cols'] = 60
        self.fields['title'].label = ''
        self.fields['title'].max_length = 100
        self.fields['title'].widget.attrs['placeholder'] = 'Tytuł ogłoszenia (max. 100 znaków)*'
        self.fields['title'].widget.attrs['size'] = 60


class CreateNewsAnswerForm(forms.ModelForm):
    class Meta:
        model = NewsAnswer
        fields = [
            'text',
            'image'
        ]

    def __init__(self, *args, **kwargs):
        super(CreateNewsAnswerForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].max_length = 4000
        self.fields['text'].widget.attrs['placeholder'] = 'Twoja odpowiedź (max. 4000 znaków)*'
        self.fields['text'].widget.attrs['rows'] = 10
        self.fields['text'].widget.attrs['cols'] = 60

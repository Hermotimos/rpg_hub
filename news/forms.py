from django import forms
from news.models import News, NewsAnswer, Survey, SurveyOption, SurveyAnswer
from users.models import Profile
from django.db.models import Q


class CreateNewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['allowed_profiles', 'image', 'text', 'title']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        self.fields['allowed_profiles'].label = ''
        self.fields['allowed_profiles'].queryset = Profile.objects.filter(
            status='active_player').exclude(user=authenticated_user)
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].max_length = 4000
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Twoje ogłoszenie (max. 4000 znaków)*'
        }
        self.fields['title'].label = ''
        self.fields['title'].max_length = 100
        self.fields['title'].widget.attrs = {
            'size': 60,
            'placeholder': 'Tytuł ogłoszenia (max. 100 znaków)*'
        }


class CreateNewsAnswerForm(forms.ModelForm):
    class Meta:
        model = NewsAnswer
        fields = ['text', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].max_length = 4000
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Twoja odpowiedź (max. 4000 znaków)*'
        }


class CreateSurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['addressees', 'image', 'text', 'title']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        self.fields['addressees'].label = ''
        self.fields['addressees'].queryset = Profile.objects.filter(
            status='active_player').exclude(user=authenticated_user)
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].max_length = 4000
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Wiadomość do ankiety (max. 4000 znaków)*'
        }
        self.fields['title'].label = ''
        self.fields['title'].max_length = 100
        self.fields['title'].widget.attrs = {
            'cols': 60,
            'placeholder': 'Tytuł ankiety (max. 100 znaków)*'
        }


class CreateSurveyOptionForm(forms.ModelForm):
    class Meta:
        model = SurveyOption
        fields = ['option_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['option_text'].label = ''
        self.fields['option_text'].max_length = 50
        self.fields['option_text'].widget.attrs = {'placeholder':  'Nowa opcja ankiety (max. 50 znaków)*'}


class ModifySurveyOptionForm(forms.ModelForm):
    class Meta:
        model = SurveyOption
        fields = ['option_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['option_text'].label = ''
        self.fields['option_text'].max_length = 50
        self.fields['option_text'].widget.attrs = {'placeholder':  'Zmieniona opcja ankiety (max. 50 znaków)*'}


class CreateSurveyAnswerForm(forms.ModelForm):
    class Meta:
        model = SurveyAnswer
        fields = ['image', 'text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = 'Załącz obraz:'
        self.fields['image'].required = False
        self.fields['text'].label = ''
        self.fields['text'].max_length = 4000
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
            'placeholder': 'Twoja odpowiedź (max. 4000 znaków)*'
        }

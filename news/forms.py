from django import forms
from news.models import Topic, News, NewsAnswer, Survey, SurveyOption, SurveyAnswer
from users.models import Profile


class CreateTopicForm(forms.ModelForm):
    
    class Meta:
        model = Topic
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].label = "Tytuł nowego tematu"

        
class CreateNewsForm(forms.ModelForm):
    
    class Meta:
        model = News
        fields = ['topic', 'title', 'allowed_profiles']
        help_texts = {
            'allowed_profiles': """
                ***Aby zaznaczyć wiele postaci - użyj CTRL albo SHIFT.<br><br>
                1) Ogłoszenie zobaczą tylko wybrani adresaci (i zawsze MG).<br>
                2) Późniejsze dodanie adresatów - wyślij MG Dezyderat.<br><br>
            """,
            'is_exclusive': 'Wykluczyć możliwość dodawania uczestników?',
        }

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        allowed_profiles = Profile.active_players.exclude(
            user=authenticated_user)

        self.fields['allowed_profiles'].label = "Adresaci"
        self.fields['title'].label = "Tytuł"
        self.fields['topic'].label = "Temat"

        self.fields['allowed_profiles'].queryset = allowed_profiles
        self.fields['allowed_profiles'].widget.attrs['size'] = min(
            len(allowed_profiles), 10)
       
class CreateNewsAnswerForm(forms.ModelForm):
    
    class Meta:
        model = NewsAnswer
        fields = ['text', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['image'].label = 'Załącz obraz'
        self.fields['text'].label = ''

        self.fields['image'].required = False
        self.fields['text'].max_length = 4000
        self.fields['text'].widget.attrs = {
            'cols': 60, 'rows': 10,
            'placeholder': 'Twoja wypowiedź (max. 4000 znaków)*'
        }


class CreateSurveyForm(forms.ModelForm):
    
    class Meta:
        model = Survey
        fields = ['addressees', 'image', 'text', 'title']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        self.fields['addressees'].label = ''
        self.fields['addressees'].queryset = Profile.active_players.exclude(user=authenticated_user)
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

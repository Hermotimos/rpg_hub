from django import forms
from news.models import News, Response
from users.models import Profile
from pagedown.widgets import PagedownWidget


class CreateNewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            'title',
            'text',
            'allowed_profiles',
            'image'
        ]

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

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )


class CreateResponseForm(forms.ModelForm):
    class Meta:
        model = Response
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


class ManageFollowedForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['followers']

    # def __init__(self, *args, **kwargs):
    #     authenticated_user = kwargs.pop('authenticated_user')
    #     super(ManageFollowedForm, self).__init__(*args, **kwargs)
    #     if authenticated_user:
    #         self.fields['followers'].queryset = Profile.objects.filter(user=authenticated_user)
    #         self.fields['followers'].label = ''

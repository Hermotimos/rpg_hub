from django import forms
from debates.models import Remark, Debate, Topic
from pagedown.widgets import PagedownWidget


class CreateRemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = [
            'text',
            'image'
        ]

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
            'title',
            'allowed_profiles',
            'is_individual'
        ]

    title = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Tytuł nowej narady (max. 100 znaków)*',
                'size': '60'
            }
        )
    )


class UpdateDebateForm(forms.ModelForm):
    class Meta:
        model = Debate
        fields = ['allowed_profiles']


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

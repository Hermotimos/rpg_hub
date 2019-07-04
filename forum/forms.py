from django import forms
from .models import Post, Topic, Board
from pagedown.widgets import PagedownWidget


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'text',
            'image'
        ]

    text = forms.CharField(
        label='',
        widget=PagedownWidget(
            attrs={
                'placeholder': 'Twój głos w naradzie (max. 4000 znaków)',
                'rows': 10,
                'cols': 60
            }
        )
    )

    image = forms.ImageField(
        label='Załącz obraz:',
        required=False,
    )


class UpdateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['allowed_profiles']


class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = [
            'topic_name',
            'allowed_profiles'
        ]

    topic_name = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Tytuł nowej narady (max. 100 znaków)',
                'size': '60'
            }
        )
    )


class CreateBoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = [
            'title',
            'description'
        ]

    title = forms.CharField(
        max_length=50,
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nowy temat narad (max. 50 znaków)',
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
                'placeholder': '[opcjonalnie] Krótki opis  (max. 100 znaków)',
                'size': '60',
            }
        )
    )

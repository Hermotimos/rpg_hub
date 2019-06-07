from django import forms

from .models import Post, Topic, Board, MultiSelectField


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'text',
        ]

    text = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Twój głos w naradzie',
                'rows': 10,
                'cols': 70
            }
        )
    )


class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = [
            'topic_name',
            'allowed_users',
            'first_post'
        ]

    topic_name = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Tytuł nowej narady',
                'size': '60'
            }
        )
    )

    first_post = forms.CharField(
        label='',
        max_length=4000,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Pierwszy głos w naradzie',
                'rows': 20,
                'cols': 70
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
                'placeholder': 'Nowy temat narad',
                'size': '60'
            }
        )
    )

    description = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Krótki opis',
                'size': '60'
            }
        )
    )

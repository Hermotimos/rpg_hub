from django import forms

from .models import Post, Topic, Board


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
                'placeholder': 'Głos w naradzie',
                'rows': 20,
                'cols': 70
            }
        )
    )


    # def clean_rpg_time(self):
    #     data = self.cleaned_data
    #     if not data.get['rpg_time']:
    #         raise forms.ValidationError('Wybierz temat narady, w której chcesz zabrać głos:')
    #     return data
    # This does not work at all. The overriden error message does not show.
    # Couldn't find answer why.


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


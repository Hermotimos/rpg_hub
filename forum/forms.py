from django import forms

from .models import Post, Topic, Board
from multiselectfield import MultiSelectField


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'topic',
            'text',
            'rpg_time'
        ]

    topic = forms.ModelChoiceField(
        label='Wybierz tytuł narady',
        queryset=Topic.objects.all(),
        # initial='-'
    )

    text = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Głos w naradzie',
                'rows': 30,
                'cols': 70
            }
        )
    )

    rpg_time = forms.CharField(
        label='Czas RPG',
        widget=forms.Textarea(
            attrs={'placeholder': 'np. 80. Jesieni 20. roku Archonatu Nemetha Samatiana',
                   'rows': 1,
                   'cols': 40
                   }
        )
    )

    def clean_rpg_time(self):
        data = self.cleaned_data
        if not data.get['rpg_time']:
            raise forms.ValidationError('Wybierz temat narady, w której chcesz zabrać głos:')
        return data
        # This does not work at all. The overriden error message does not show.
        # Couldn't find answer why.


class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = [
            'board',
            'topic_name',
            'allowed_users'
        ]

    board = forms.ModelChoiceField(
        label='Wybierz temat narady:',
        queryset=Board.objects.all()
    )

    topic_name = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Tytuł narady',
                'size': '60'
            }
        )
    )


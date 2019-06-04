from django import forms

from .models import Post, Topic


class CreatePostForm(forms.ModelForm):
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
    topic = forms.ModelChoiceField(
        label='Wybierz tytuł narady',
        queryset=Topic.objects.all()
    )
    rpg_time = forms.CharField(
        label='Data',
        widget=forms.Textarea(
            attrs={'placeholder': 'np. 80. Jesieni 20. roku Archonatu Nemetha Samatiana',
                   'rows': 1,
                   'cols': 40
                   }
        )
    )

    class Meta:
        model = Post
        fields = [
            'topic',
            'text',
            'rpg_time'
        ]

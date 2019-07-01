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
                'placeholder': 'Twój głos w naradzie (max. 4000 znaków)',
                'rows': 10,
                'cols': 60
            }
        )
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
            'allowed_profiles',
            'first_post'
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

    first_post = forms.CharField(
        label='',
        max_length=4000,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Pierwszy głos w naradzie (max. 4000 znaków)',
                'rows': 10,
                'cols': 60
            }
        )
    )

    def save(self, commit=True):
        topic = super(CreateTopicForm, self).save(commit=False)
        if commit:
            # for profile in self.cleaned_data['allowed_profiles']:
            #     topic.allowed_profiles.add(profile)
            topic.save()
            topic.allowed_profiles.set(self.cleaned_data['allowed_profiles'])
        return topic


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

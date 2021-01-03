from django import forms
from django.forms.widgets import HiddenInput
from django.db.models import Q

from debates.models import Remark, Debate, Topic
from users.models import Profile
from users.models import User


class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CreateDebateForm(forms.ModelForm):
    class Meta:
        model = Debate
        fields = ['name', 'known_directly', 'is_individual']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        if authenticated_user.profile.status != 'gm':
            self.fields['is_individual'].widget = HiddenInput()
            
        self.fields['known_directly'].queryset = Profile.objects.exclude(
            Q(user=authenticated_user)
            | Q(status__icontains='dead')
            | Q(status='gm')
        ).select_related()
        self.fields['known_directly'].widget.attrs['size'] = 10


class CreateRemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = ['author', 'text', 'image']

    def __init__(self, *args, **kwargs):
        debate_id = kwargs.pop('debate_id')
        if debate_id:
            debate = Debate.objects.get(id=debate_id)
            debate_known_directly = debate.known_directly.all()
        else:
            debate_known_directly = Profile.objects.exclude(status__icontains='dead')
            
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        if authenticated_user.profile.status != 'gm':
            self.fields['author'].widget = HiddenInput()
        else:
            self.fields['author'].queryset = User.objects.filter(
                Q(profile__status='gm') | Q(profile__in=debate_known_directly)
            ).order_by('profile__name')
            
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs = {
            'cols': 60,
            'rows': 10,
        }

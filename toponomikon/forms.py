from django import forms
from toponomikon.models import GeneralLocation, SpecificLocation
from users.models import Profile
from django.db.models import Q


class GeneralLocationInformForm(forms.ModelForm):
    class Meta:
        model = GeneralLocation
        fields = ['known_indirectly']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        already_known_directly = kwargs.pop('known_directly_old')
        already_known_indirectly = kwargs.pop('known_indirectly_old')
        super().__init__(*args, **kwargs)
        self.fields['known_indirectly'].label = ''
        self.fields['known_indirectly'].queryset = Profile.objects.exclude(Q(user=authenticated_user) |
                                                                           Q(character_status='dead_player') |
                                                                           Q(character_status='dead_npc') |
                                                                           Q(character_status='living_npc') |
                                                                           Q(character_status='gm') |
                                                                           Q(id__in=already_known_directly) |
                                                                           Q(id__in=already_known_indirectly))
        self.fields['known_indirectly'].widget.attrs = {'size': 10}


class SpecificLocationInformForm(forms.ModelForm):
    class Meta:
        model = SpecificLocation
        fields = ['known_indirectly']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        already_known_directly = kwargs.pop('known_directly_old')
        already_known_indirectly = kwargs.pop('known_indirectly_old')
        super().__init__(*args, **kwargs)
        self.fields['known_indirectly'].label = ''
        self.fields['known_indirectly'].queryset = Profile.objects.exclude(Q(user=authenticated_user) |
                                                                           Q(character_status='dead_player') |
                                                                           Q(character_status='dead_npc') |
                                                                           Q(character_status='living_npc') |
                                                                           Q(character_status='gm') |
                                                                           Q(id__in=already_known_directly) |
                                                                           Q(id__in=already_known_indirectly))
        self.fields['known_indirectly'].widget.attrs = {'size': 10}

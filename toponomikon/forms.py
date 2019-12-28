from django import forms
from toponomikon.models import GeneralLocation, SpecificLocation
from users.models import Profile
from django.db.models import Q


class ToponomikonInformForm(forms.ModelForm):
    class Meta:
        model = GeneralLocation
        fields = ['known_indirectly']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        already_know_directly = kwargs.pop('known_directly')
        already_know_indirectly = kwargs.pop('known_indirectly')
        super(ToponomikonInformForm, self).__init__(*args, **kwargs)
        informable_profiles = Profile.objects.exclude(Q(user=authenticated_user) |
                                                      Q(character_status='dead_player') |
                                                      Q(character_status='dead_npc') |
                                                      Q(character_status='living_npc') |
                                                      Q(character_status='gm') |
                                                      Q(id__in=already_know_directly) |
                                                      Q(id__in=already_know_indirectly))
        self.fields['known_indirectly'].label = ''
        self.fields['known_indirectly'].queryset = informable_profiles\
        #     .exclude(
        #     id__in=[p.id for p in already_allowed_profiles]
        # )
        self.fields['known_indirectly'].widget.attrs['size'] = 10

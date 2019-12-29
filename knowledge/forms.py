from django import forms
from knowledge.models import KnowledgePacket
from users.models import Profile
from django.db.models import Q


class KnowledgePacketInformForm(forms.ModelForm):
    class Meta:
        model = KnowledgePacket
        fields = ['allowed_profiles']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        already_allowed_profiles = kwargs.pop('already_allowed_profiles')
        super(KnowledgePacketInformForm, self).__init__(*args, **kwargs)
        self.fields['allowed_profiles'].label = ''
        self.fields['allowed_profiles'].queryset = Profile.objects.exclude(Q(user=authenticated_user) |
                                                                           Q(character_status='dead_player') |
                                                                           Q(character_status='dead_npc') |
                                                                           Q(character_status='living_npc') |
                                                                           Q(character_status='gm') |
                                                                           Q(id__in=already_allowed_profiles))
        self.fields['allowed_profiles'].widget.attrs = {'size': 10}

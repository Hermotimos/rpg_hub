from django import forms
from django.db.models import Q

from characters.models import Character
from knowledge.models import KnowledgePacket


class KnowledgePacketInformForm(forms.ModelForm):
    """Source: https://stackoverflow.com/questions/2216974/django-modelform-for-many-to-many-fields"""
    class Meta:
        model = KnowledgePacket
        fields = []

    # this creates sth like new field on the model to use in this form:
    characters = forms.ModelMultipleChoiceField(
        queryset=Character.objects.exclude(Q(profile__character_status='dead_player') |
                                           Q(profile__character_status='dead_npc') |
                                           Q(profile__character_status='living_npc') |
                                           Q(profile__character_status='gm'))
    )

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        allowed_characters_old = kwargs.pop('allowed_characters_old')
        super(KnowledgePacketInformForm, self).__init__(*args, **kwargs)

        # Code from the source of this solution, not used now
        # if kwargs.get('instance'):
        #     initial = kwargs.setdefault('initial', {})
        #     initial['characters'] = [ch.pk for ch in kwargs['instance'].characters.all()]
        # kn_pakcet = kwargs.get('instance')
        # print(type(kn_pakcet))
        # forms.ModelForm.__init__(self, *args, **kwargs)

        self.fields['characters'].queryset = Character.objects.exclude(Q(profile__user=authenticated_user) |
                                                                       Q(id__in=allowed_characters_old))

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)

        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            instance.characters.clear()
            instance.characters.add(*self.cleaned_data['characters'])

        self.save_m2m = save_m2m

        if commit:
            instance.save()
            self.save_m2m()

        return instance

    # SIMPLER SAVE (from the source, maybe use later)
    # def save(self):
    #     instance = forms.ModelForm.save(self)
    #     instance.characters.clear()
    #     instance.characters.add(*self.cleaned_data['characters'])
    #     return instance

    # OLD FORM:
    # class Meta:
    #     model = KnowledgePacket
    #     fields = ['characters']
    #
    # def __init__(self, *args, **kwargs):
    #     authenticated_user = kwargs.pop('authenticated_user')
    #     already_allowed_profiles = kwargs.pop('already_allowed_profiles')
    #     super(KnowledgePacketInformForm, self).__init__(*args, **kwargs)
    #     self.fields['allowed_profiles'].label = ''
    #     self.fields['allowed_profiles'].queryset = Profile.objects.exclude(Q(user=authenticated_user) |
    #                                                                        Q(character_status='dead_player') |
    #                                                                        Q(character_status='dead_npc') |
    #                                                                        Q(character_status='living_npc') |
    #                                                                        Q(character_status='gm') |
    #                                                                        Q(id__in=already_allowed_profiles))
    #     self.fields['allowed_profiles'].widget.attrs = {'size': 10}

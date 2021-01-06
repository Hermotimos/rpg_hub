from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.db.models import Q

from contact.models import Demand, DemandAnswer, Plan
from users.models import User, Profile


# ------------------- DEMANDS -------------------


class DemandsCreateForm(forms.ModelForm):
    
    class Meta:
        model = Demand
        fields = ['addressee', 'text', 'image']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        # self.fields['addressee'].queryset = User.objects.exclude(
        #     Q(id=authenticated_user.id)
        #     | Q(profile__status='dead_player')
        #     | Q(profile__status='inactive_player')
        #     | Q(profile__status='dead_npc')
        #     | Q(profile__status='living_npc')
        # ).order_by('username')
        print(Profile.contactables.all())
        self.fields['addressee'].queryset = Profile.contactables.exclude(
            id=authenticated_user.profile.id)
        
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Wyślij dezyderat', css_class='btn-dark'))


class DemandAnswerForm(forms.ModelForm):
    
    class Meta:
        model = DemandAnswer
        fields = ['text', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].label = ''


# ------------------- PLANS -------------------


class PlanForm(forms.ModelForm):
    
    class Meta:
        model = Plan
        fields = ['inform_gm', 'text', 'image']
        help_texts = {
            'inform_gm': """
                Wiedza MG może wpłynąć na szanse powodzenia planu tylko w
                granicach uprzednio przyjętych realiów. Celem nie będzie nigdy
                ukrócenie śmiałych planów. Jeśli obawiasz się, że może być
                inaczej, utrzymaj plan w tajemnicy!
            """,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zmiana planów', css_class='btn-dark'))

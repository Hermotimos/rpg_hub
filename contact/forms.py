from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from contact.models import Demand, DemandAnswer, Plan
from users.models import Profile

from django.db.models.query_utils import Q
# ------------------- DEMANDS -------------------


class DemandsCreateForm(forms.ModelForm):
    
    class Meta:
        model = Demand
        fields = ['addressee', 'text', 'image']

    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        profile = authenticated_user.profile
        super().__init__(*args, **kwargs)
        
        addressees = Profile.contactables.exclude(id=profile.id)
        if authenticated_user.profile.status == 'player':
            gms = addressees.filter(status='gm')
            addressees = addressees.filter(id__in=profile.characters_known_directly.all())
            addressees = (addressees | gms)
        elif authenticated_user.profile.status == 'npc':
            addressees = addressees.filter(status='gm')
            
        self.fields['addressee'].queryset = addressees
        
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
            Submit('submit', 'Zapisz plan', css_class='btn-dark'))

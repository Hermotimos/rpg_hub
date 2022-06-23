from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from contact.models import Demand, DemandAnswer, Plan
from users.models import Profile


# ------------------- DEMANDS -------------------


class DemandsCreateForm(forms.ModelForm):
    
    class Meta:
        model = Demand
        fields = ['addressee', 'text', 'image']

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        super().__init__(*args, **kwargs)

        self.fields['addressee'].label = "Adresat"
        self.fields['image'].label = "Załącz obraz"
        self.fields['text'].label = "Tekst"

        addressees = Profile.contactables.exclude(id=profile.id)
        gms = addressees.filter(status='gm')
        if profile.status == 'player':
            addressees = addressees.filter(
                character__in=profile.character.acquaintaned_to.all())
            addressees = (addressees | gms)
        elif profile.status == 'npc':
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
        
        self.fields['image'].label = "Załącz obraz"
        self.fields['inform_gm'].label = "Poinformuj MG?"
        self.fields['text'].label = "Tekst"

        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', 'Zapisz plan', css_class='btn-dark'))

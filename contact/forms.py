from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.db.models import Q

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

        if profile.status == 'gm':
            addressees = Profile.players.all()   # TODO change to active when moved to communications
        elif profile.status == 'player':
            addressees = Profile.contactables.filter(
                Q(character__in=profile.character.acquaintances.all()) | Q(status='gm'))
        else:
            addressees = Profile.objects.none()

        # TODO temp 'Ilen z Astinary, Alora z Astinary, Syngir, Murkon'
        # hide Davos from Ilen and Alora
        if profile.id in [5, 6]:
            addressees = addressees.exclude(id=3)
        # vice versa
        if profile.id == 3:
            addressees = addressees.exclude(id__in=[5, 6])
        # hide Syngir from Murkon and vice versa
        if profile.id in [82, 93]:
            addressees = addressees.exclude(id__in=[82, 93])
        # TODO end temp
        
        self.fields['addressee'].queryset = addressees.exclude(id=profile.id)
        
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

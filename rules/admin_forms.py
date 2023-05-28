from django import forms

from rules.models import ConditionalModifier, Domain, Modifier, Spell


class ConditionalModifierAdminForm(forms.ModelForm):
    """Custom form for query optimization."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['modifier'].queryset = Modifier.objects.select_related('factor')

    class Meta:
        model = ConditionalModifier
        exclude = []


# -----------------------------------------------------------------------------


class DomainAdminAdminForm(forms.ModelForm):
    """Custom form for adding color input."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].help_text = """
            <a href="https://www.w3schools.com/colors/colors_picker.asp" target="_blank">
                https://www.w3schools.com/colors/colors_picker.asp
            </a>"""

    class Meta:
        model = Domain
        exclude = []
        widgets = {'color': forms.TextInput(attrs={'type': 'color'})}


# -----------------------------------------------------------------------------


class SpellForm(forms.ModelForm):

    class Meta:
        model = Spell
        help_texts = {
            'range': "Zasięg w metrach",
            'radius': "Promień w metrach",
            'duration': "Czas w sekundach (360 s = 1 m, 3600 s = 1 h)",
            'effect_description': "Efekty do amplifikacji w klamrze {...}!",
        }
        exclude = ()

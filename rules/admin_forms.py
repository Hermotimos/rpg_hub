from django import forms

from rules.models import ConditionalModifier, Domain, Modifier


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

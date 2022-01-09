from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.db.models import Q
from django.forms.widgets import HiddenInput, TextInput

from communications.models import ThreadTag, Statement, Option, \
    Announcement, Debate, Thread
from users.models import Profile


class ThreadTagEditForm(forms.ModelForm):
    """A form for editing a Tag for formset ThreadTagEditFormSet."""

    class Meta:
        model = ThreadTag
        fields = ['title', 'color', 'author', 'kind']
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['author'].widget = forms.HiddenInput()
        self.fields['kind'].widget = forms.HiddenInput()
        

class ThreadTagEditFormSetHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.add_input(
            Submit('submit', 'Zapisz', css_class='btn-dark d-block mx-auto'))
        self.form_show_labels = False
        self.layout = Layout(
            Row(
                Column(
                    'title', '', css_class='form-group col-sm-7 mb-0',
                    title="Nowy tag"),
                Column(
                    'color', '', css_class='form-group col-sm-3 mb-0',
                    title="Podaj kod koloru"),
                Column(
                    'DELETE', css_class='form-group col-sm-1 mb-0 mt-2',
                    title="Usunąć tag?"),
            ))
        

ThreadTagEditFormSet = forms.modelformset_factory(
    model=ThreadTag, form=ThreadTagEditForm, exclude=[], extra=2, can_delete=True)


# ===========================================================================


class AnnouncementCreateForm(forms.ModelForm):
    
    class Meta:
        model = Announcement
        fields = ['title', 'known_directly']
        
    def __init__(self, *args, **kwargs):
        current_profile = kwargs.pop('current_profile')
        super().__init__(*args, **kwargs)

        self.fields['known_directly'].help_text = """
            ***Aby zaznaczyć wiele postaci - użyj CTRL albo SHIFT.<br><br>
            1) Ogłoszenie zobaczą tylko wybrani adresaci (i zawsze MG).<br>
            2) Późniejsze dodanie adresatów - wyślij MG Dezyderat.<br><br>
        """
        
        self.fields['known_directly'].label = "Adresaci"
        self.fields['title'].label = "Tytuł"

        known_directly = Profile.contactables.exclude(id=current_profile.id)
        self.fields['known_directly'].queryset = known_directly
        self.fields['known_directly'].widget.attrs['size'] = min(
            len(known_directly), 10)
        

class DebateCreateForm(forms.ModelForm):
    
    class Meta:
        model = Debate
        fields = ['title', 'known_directly', 'is_exclusive']
        
    def __init__(self, *args, **kwargs):
        current_profile = kwargs.pop('current_profile')
        super().__init__(*args, **kwargs)

        self.fields['is_exclusive'].help_text = """
            Wykluczyć możliwość dodawania uczestników?'"""
        self.fields['known_directly'].help_text = """
            ***Aby zaznaczyć wiele postaci - użyj CTRL albo SHIFT.<br><br>
            1) Włączaj tylko postacie znajdujące się w pobliżu w chwili
                zakończenia ostatniej sesji.<br>
            2) Postacie w pobliżu niewłączone do narady mogą to zauważyć.<br>
            3) Jeśli chcesz zaczekać na sposobny moment, powiadom MG.<br>
            4) Jeśli na liście brakuje postaci, powiadom MG.<br><br>"""

        self.fields['is_exclusive'].label = "Narada zamknięta?"
        self.fields['known_directly'].label = "Uczestnicy"
        self.fields['title'].label = "Tytuł"

        known_directly = Profile.living.all()

        if current_profile.status != 'gm':
            self.fields['is_exclusive'].widget = HiddenInput()
            known_directly = known_directly.filter(
                character__in=current_profile.characters_known_directly.all()
            ).exclude(id=current_profile.id).select_related()

        self.fields['known_directly'].queryset = known_directly

        self.fields['known_directly'].widget.attrs['size'] = min(
            len(known_directly), 10)


class ThreadEditTagsForm(forms.ModelForm):
    """A form for editing Tags within a single Thread."""
    
    class Meta:
        model = Thread
        fields = ['tags']
    
    def __init__(self, *args, **kwargs):
        tags = kwargs.pop('tags')
        super().__init__(*args, **kwargs)
        
        self.fields['tags'].label = ""
        self.fields['tags'].queryset = tags
        self.fields['tags'].widget.attrs['size'] = \
            len(tags) if len(tags) < 15 else 15
        
        self.helper = FormHelper()
        self.helper.add_input(
            Submit(
                'submit', 'Zapisz',
                css_class='btn-dark d-block mx-auto mt-3 mb-n3'))


class StatementCreateForm(forms.ModelForm):
    
    class Meta:
        model = Statement
        fields = ['author', 'text', 'image']
    
    def __init__(self, *args, **kwargs):
        current_profile = kwargs.pop('current_profile')
        thread_kind = kwargs.pop('thread_kind')
        known_directly = kwargs.pop('known_directly')
        super().__init__(*args, **kwargs)
        
        self.fields['author'].label = "Autor"
        self.fields['image'].label = "Załącz obraz"
        self.fields['text'].label = ""
        
        if current_profile.status != 'gm':
            self.fields['author'].widget = HiddenInput()
        else:
            self.fields['author'].queryset = Profile.objects.filter(
                Q(status='gm') | Q(id__in=known_directly))
            
        if thread_kind != "Debate":
            self.fields['author'].widget = HiddenInput()
        self.fields['text'].widget.attrs = {
            'cols': 60, 'rows': 10, 'placeholder': 'Twoja wypowiedź*'}


class OptionCreateForm(forms.ModelForm):
    # TODO Separate view and template reached by means of a "+option" button
    
    class Meta:
        model = Option
        fields = ['text']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['text'].label = ""
        self.fields['text'].max_length = 50
        self.fields['text'].widget.attrs = {
            'placeholder': 'Opcja w ankiecie (max. 50 znaków)*'}

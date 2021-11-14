from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.db.models import Q
from django.forms.widgets import HiddenInput

from communications.models import Topic, ThreadTag, Statement, Option, \
    Announcement, Debate
from users.models import Profile


class TopicCreateForm(forms.ModelForm):
    
    class Meta:
        model = Topic
        fields = ['title']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].label = "Tytuł nowego tematu"


class ThreadTagEditForm(forms.ModelForm):
    
    class Meta:
        model = ThreadTag
        fields = ['title', 'color', 'author', 'kind']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['color'].label = "Kolor"
        self.fields['title'].label = ""

        self.fields['author'].widget = forms.HiddenInput()
        self.fields['kind'].widget = forms.HiddenInput()
        self.fields['title'].widget.attrs = {'placeholder': 'Tag*'}
        

ThreadTagEditFormSet = forms.modelformset_factory(
    model=ThreadTag,
    form=ThreadTagEditForm,
    fields=['title', 'color', 'kind', 'author'],
    extra=2,
    can_delete=True)


class ThreadTagEditFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(
            Submit('submit', 'Zapisz', css_class='btn-dark d-block mx-auto'))
        self.form_show_labels = False
        self.layout = Layout(Row(
            Column(
                'title', '', placeholder="Nowy tag*",
                css_class='form-group col-sm-7 mb-0'),
            Column(
                'color', '', css_class='form-group col-sm-3 mb-0',
                title="Podaj kod koloru"),
            # Column(
            #     'author', '', css_class='form-group col-sm-3 mb-0',
            #     title="Podaj kod koloru"),
            Column(
                'DELETE', css_class='form-group col-sm-1 mb-0 mt-2',
                title="Usunąć tag?"),
        ))
        
        
class AnnouncementCreateForm(forms.ModelForm):
    
    class Meta:
        model = Announcement
        fields = ['topic', 'title', 'known_directly']
        
    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        super().__init__(*args, **kwargs)

        self.fields['known_directly'].help_text = """
            ***Aby zaznaczyć wiele postaci - użyj CTRL albo SHIFT.<br><br>
            1) Ogłoszenie zobaczą tylko wybrani adresaci (i zawsze MG).<br>
            2) Późniejsze dodanie adresatów - wyślij MG Dezyderat.<br><br>
        """
        
        self.fields['known_directly'].label = "Adresaci"
        self.fields['title'].label = "Tytuł"
        self.fields['topic'].label = "Temat"

        known_directly = Profile.active_players.exclude(id=profile.id)
        self.fields['known_directly'].queryset = known_directly
        self.fields['known_directly'].widget.attrs['size'] = min(
            len(known_directly), 10)

    
class DebateCreateForm(forms.ModelForm):
    
    class Meta:
        model = Debate
        fields = ['topic', 'title', 'known_directly', 'is_exclusive']
        
    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
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
        self.fields['topic'].label = "Temat"

        topic_qs = Topic.objects.all()
        known_directly = Profile.living.all()

        if profile.status != 'gm':
            self.fields['is_exclusive'].widget = HiddenInput()
    
            topic_id = kwargs['initial']['topic'].id \
                if kwargs['initial']['topic'] else None
            topic_qs = topic_qs.filter(
                Q(debates__known_directly=profile) | Q(id=topic_id)
            ).distinct()
    
            known_directly = known_directly.filter(
                character__in=profile.characters_known_directly.all()
            ).exclude(id=profile.id).select_related()

        self.fields['topic'].queryset = topic_qs
        self.fields['known_directly'].queryset = known_directly

        self.fields['known_directly'].widget.attrs['size'] = min(
            len(known_directly), 10)


class StatementCreateForm(forms.ModelForm):
    
    class Meta:
        model = Statement
        fields = ['author', 'text', 'image']
    
    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        thread_kind = kwargs.pop('thread_kind')
        known_directly = kwargs.pop('known_directly')
        super().__init__(*args, **kwargs)
        
        self.fields['author'].label = "Autor"
        self.fields['image'].label = "Załącz obraz"
        self.fields['text'].label = ""
        
        if profile.status != 'gm':
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

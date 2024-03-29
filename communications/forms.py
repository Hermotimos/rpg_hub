import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django.db.models import Q
from django.forms import (
    ModelChoiceField,
    ModelForm,
    HiddenInput,
    TextInput,
    modelformset_factory
)

from communications.models import ThreadTag, Statement, Option, \
    Announcement, Debate, Thread
from users.models import Profile, User


class ThreadTagEditForm(ModelForm):
    """A form for editing a Tag for formset ThreadTagEditFormSet."""

    class Meta:
        model = ThreadTag
        fields = ['title', 'color', 'author', 'kind']
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['author'].widget = HiddenInput()
        self.fields['kind'].widget = HiddenInput()


class ThreadTagEditFormSetHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_input(Submit('submit', 'Zapisz', css_class='btn-dark d-block mx-auto'))
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


ThreadTagEditFormSet = modelformset_factory(
    model=ThreadTag, form=ThreadTagEditForm, exclude=[], extra=2, can_delete=True)


# ===========================================================================


class AnnouncementCreateForm(ModelForm):

    class Meta:
        model = Announcement
        fields = ['title', 'participants']

    def __init__(self, *args, **kwargs):
        current_profile = kwargs.pop('current_profile')
        super().__init__(*args, **kwargs)

        self.fields['participants'].help_text = """
            ✧ Aby zaznaczyć wiele Postaci - użyj CTRL albo SHIFT.<br>
            ✧ MG jest dołączany automatycznie do wszystkich Ogłoszeń.<br><br>
        """

        self.fields['participants'].label = "Adresaci"
        self.fields['title'].label = "Tytuł"

        # Show profiles' Users as options (translated to Profiles in the view)
        participants = User.objects.filter(
            profiles__in=Profile.contactables.exclude(id=current_profile.id),
            profiles__character__in=current_profile.character.acquaintances.all(),
        ).distinct()

        self.fields['participants'].queryset = participants
        self.fields['participants'].widget.attrs['size'] = min(
            len(participants), 10)


class DebateCreateForm(ModelForm):
    from chronicles.models import GameEvent
    game_event = ModelChoiceField(
        queryset=GameEvent.objects.order_by('-id'),
        required=False,
        label='Wydarzenie',
    )

    class Meta:
        model = Debate
        fields = ['title', 'game_event', 'participants', 'is_exclusive']

    def __init__(self, *args, **kwargs):
        from prosoponomikon.models import AcquaintanceshipProxy
        current_profile = kwargs.pop('current_profile')
        super().__init__(*args, **kwargs)

        self.fields['is_exclusive'].help_text = """
            Wykluczyć możliwość dodawania uczestników?'"""
        self.fields['participants'].help_text = """
            ✧ Aby zaznaczyć wiele Postaci - użyj CTRL albo SHIFT.<br><br>
            ✧ Dołączaj tylko Postacie znajdujące się w pobliżu w chwili zakończenia ostatniej sesji
                (Postacie znajdujące się w pobliżu a niewłączone do narady mogą to zauważyć;
                jeśli chcesz zaczekać na sposobny moment, powiadom MG).<br><br>"""

        self.fields['is_exclusive'].label = "Narada zamknięta?"
        self.fields['participants'].label = "Uczestnicy"
        self.fields['title'].label = "Tytuł"

        # Show profiles' Acquaintanceships as options (translated to Profiles in the view)
        participants = AcquaintanceshipProxy.objects.filter(
            knowing_character=current_profile.character
        ).exclude(
            known_character=current_profile.character
        ).select_related('known_character')

        # TODO temp 'Ilen z Astinary, Alora z Astinary'
        # hide Davos from Ilen and Alora
        if current_profile.id in [5, 6]:
            participants = participants.exclude(known_character__profile__id=3)
        # vice versa
        if current_profile.id == 3:
            participants = participants.exclude(known_character__profile__id__in=[5, 6])
        # TODO end temp

        self.fields['participants'].queryset = participants.order_by(
            '-known_character__profile__status', 'known_character__fullname')

        if current_profile.status != 'gm':
            self.fields['is_exclusive'].widget = HiddenInput()
            self.fields['game_event'].widget = HiddenInput()
        self.fields['participants'].widget.attrs['size'] = min(
            len(participants), 10)


class ThreadEditTagsForm(ModelForm):
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


class StatementCreateForm(ModelForm):

    class Meta:
        model = Statement
        fields = ['author', 'text', 'image']

    def __init__(self, *args, **kwargs):
        current_profile = kwargs.pop('current_profile')
        thread_kind = kwargs.pop('thread_kind')
        participants = kwargs.pop('participants')
        super().__init__(*args, **kwargs)

        self.fields['author'].label = "Autor"
        self.fields['image'].label = "Załącz obraz"
        self.fields['text'].label = ""

        if thread_kind != "Debate" or current_profile.status != 'gm':
            self.fields['author'].widget = HiddenInput()
        else:
            # If Thread doesn't exist yet, meaning this form is used along
            # thread create form, put all profiles in author choice list
            if not participants:
                self.fields['author'].queryset = Profile.gm_controlled.select_related('character')
            else:
                self.fields['author'].queryset = Profile.objects.filter(
                    Q(status='gm') | Q(id__in=participants)).select_related('character')

    def save(self, commit=True, **kwargs):
        """Override TinyMCE default behavior, which is that lists loose
         indentation given by the user.
        """
        if not commit:
            instance = super().save(commit=False)
            text = instance.text
            replacements = {
                '<ol>': '<ol class="ml-2">', '<ul>': '<ul class="ml-2">',
                '<li>': '<li class="ml-3">',
            }
            for k, v in replacements.items():
                text = text.replace(k, v)
            if kwargs.get('thread_kind') == "Debate":
                # Remove HTML tags except for p from Statements in Debates
                clean = re.compile(r'<(?!p).*?>')
                text = re.sub(clean, '', text)
            instance.text = text
            return instance
        else:
            return super().save()


class OptionCreateForm(ModelForm):
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

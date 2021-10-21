from django import forms
from communications.models import Topic, Thread
from users.models import Profile


class CreateTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['title'].label = "Tytuł nowego tematu"


class CreateThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['topic', 'title', 'known_directly']
        help_texts = {
            'known_directly': """
                ***Aby zaznaczyć wiele postaci - użyj CTRL albo SHIFT.<br><br>
                1) Ogłoszenie zobaczą tylko wybrani adresaci (i zawsze MG).<br>
                2) Późniejsze dodanie adresatów - wyślij MG Dezyderat.<br><br>
            """,
            'is_exclusive': 'Wykluczyć możliwość dodawania uczestników?', # TODO ?????
        }
    
    def __init__(self, *args, **kwargs):
        authenticated_user = kwargs.pop('authenticated_user')
        super().__init__(*args, **kwargs)
        known_directly = Profile.active_players.exclude(
            user=authenticated_user)
        
        self.fields['known_directly'].label = "Adresaci"
        self.fields['title'].label = "Tytuł"
        self.fields['topic'].label = "Temat"
        
        self.fields['known_directly'].queryset = known_directly
        self.fields['known_directly'].widget.attrs['size'] = min(
            len(known_directly), 10)

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegistrationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    email = forms.EmailField(required=False)


class UserUpdateForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['username', 'email']

    email = forms.EmailField(required=False)


class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ['name', 'image']

    # With this there's error: 'ProfileUpdateForm' object has no attribute 'get'
    # def __init__(self, *args, **kwargs):
    #     super(ProfileUpdateForm, self).__init__(self, *args, **kwargs)
    #     self.fields['name'].label = ''
    #     self.fields['name'].max_length = 50
    #     self.fields['name'].widget.attrs['placeholder'] = 'max. 50 znaków (spacje dozwolone)'
    #     self.fields['name'].widget.attrs['size'] = 60
    #     self.fields['image'].label = 'Awatar'

    name = forms.CharField(
        label='Imię postaci (wyświetlane przy postach)',
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'max. 50 znaków (spacje dozwolone)',
                'size': '60'
            }
        )
    )
    image = forms.ImageField(
        label='Awatar'
    )

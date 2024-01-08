from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.forms import ModelForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username',)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, label='username / email')
    password = forms.CharField(max_length=50, 
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
from django import forms
from django.contrib.auth.models import User

class SubscriberForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'email@example.com'
        })
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Leave blank to keep current password'
        })
    )
    plan = forms.ChoiceField(
        choices=[
            ('free', 'Free'),
            ('pro', 'Pro'),
            ('enterprise', 'Enterprise'),
        ],
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    status = forms.ChoiceField(
        choices=[
            ('active', 'Active'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired'),
        ],
        widget=forms.Select(attrs={'class': 'form-input'})
    )
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, BillingInfo

class RegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    password = forms.CharField(widget=forms.PasswordInput(), required=False, label="New Password")
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False, label="Confirm New Password")
    
    class Meta:
        model = User
        fields = ('username', 'email')
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password:
            if not password2:
                raise ValidationError({'password2': "Please confirm your new password."})
            if password != password2:
                raise ValidationError({'password2': "Passwords don't match."})
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class BillingInfoForm(forms.ModelForm):
    """Form for managing billing information"""
    class Meta:
        model = BillingInfo
        fields = ('card_number', 'expiry_date', 'cvv', 'billing_address')
        widgets = {
            'card_number': forms.TextInput(attrs={'placeholder': '0000 0000 0000 0000'}),
            'expiry_date': forms.TextInput(attrs={'placeholder': 'MM/YYYY'}),
            'cvv': forms.TextInput(attrs={'placeholder': '123'}),
            'billing_address': forms.Textarea(attrs={'rows': 3}),
        }

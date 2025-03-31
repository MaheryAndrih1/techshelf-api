from django import forms
from .models import Store, StoreTheme, Rating

class StoreCreationForm(forms.ModelForm):
    """Form for creating a new store"""
    class Meta:
        model = Store
        fields = ['store_name', 'subdomain_name']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subdomain_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_subdomain_name(self):
        subdomain = self.cleaned_data.get('subdomain_name')
        # If subdomain is empty, it will be generated from the store name in the model's save method
        if subdomain and Store.objects.filter(subdomain_name=subdomain).exists():
            raise forms.ValidationError("This subdomain is already taken.")
        return subdomain


class StoreEditForm(forms.ModelForm):
    """Form for editing an existing store"""
    class Meta:
        model = Store
        fields = ['store_name', 'subdomain_name']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control'}),
            'subdomain_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_subdomain_name(self):
        subdomain = self.cleaned_data.get('subdomain_name')
        # Make sure the subdomain is unique, but exclude the current store
        if subdomain:
            existing_stores = Store.objects.filter(subdomain_name=subdomain)
            if self.instance and self.instance.pk:
                existing_stores = existing_stores.exclude(pk=self.instance.pk)
            if existing_stores.exists():
                raise forms.ValidationError("This subdomain is already taken.")
        return subdomain


class StoreThemeForm(forms.ModelForm):
    """Form for editing a store theme"""
    class Meta:
        model = StoreTheme
        fields = ['primary_color', 'secondary_color', 'font', 'logo_url', 'banner_url']
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'font': forms.Select(attrs={'class': 'form-select'}),
        }


class RatingForm(forms.ModelForm):
    """Form for rating a store"""
    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.RadioSelect(choices=[(i, f"{i} stars") for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

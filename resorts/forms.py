from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Resort, Booking

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    is_resort_owner = forms.BooleanField(required=False, label='Register as Resort Owner')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone', 'address', 'is_resort_owner')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ResortForm(forms.ModelForm):
    class Meta:
        model = Resort
        fields = ['name', 'description', 'location', 'price_per_night', 'image', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price_per_night': forms.NumberInput(attrs={'min': 0}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise forms.ValidationError('Check-out date must be after check-in date')
        return cleaned_data

class BookingResponseForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status', 'rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
        }

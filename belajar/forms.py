from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # HAPUS 'kelas' dari sini, sisakan 'foto' saja
        fields = ['foto']
        widgets = {
            'foto': forms.FileInput(attrs={'class': 'hidden'}), # Class 'hidden' karena kita pakai tombol custom di UI
        }
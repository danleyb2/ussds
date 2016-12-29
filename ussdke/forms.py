from .models import USSD
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.admin import User

class USSDForm(forms.ModelForm):
    class Meta:
        model=USSD
        fields= ['description',]

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


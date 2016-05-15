from .models import USSD

from django.forms import ModelForm


class USSDForm(ModelForm):
    class Meta:
        model=USSD
        fields= ['description',]

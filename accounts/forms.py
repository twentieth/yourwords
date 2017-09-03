from django import forms
from .models import Option
from django.utils.translation import ugettext, ugettext_lazy as _


class OptionForm(forms.ModelForm):

    extended_searching = forms.BooleanField(label=_('Wyszukuj słówka, używając rozszerzonego algorytmu wyszukiwania'), required=False)

    class Meta:
        model = Option
        fields = ('extended_searching',)
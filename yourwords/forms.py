import re
from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms
from .models import English
from .models import Contact


class AddRecordForm(forms.ModelForm):
    polish = forms.CharField(widget=forms.TextInput(attrs={'id': 'input_polish', 'class': 'w3-input w3-border', 'placeholder': _('pole wymagane')}), error_messages={'required': 'pole jest wymagane', 'max_length': _('Pole może zawierać maksymalnie 100 znaków.')})
    english = forms.CharField(widget=forms.TextInput(attrs={'id': 'input_english', 'class': 'w3-input w3-border', 'placeholder': _('pole wymagane')}), error_messages={'required': 'pole jest wymagane', 'max_length': _('Pole może zawierać maksymalnie 100 znaków.')})
    sentence = forms.CharField(required=False, widget=forms.Textarea(attrs={'id': 'input_sentence', 'class': 'w3-input w3-border', 'rows': '5'}), error_messages={'max_length': _('Pole może zawierać maksymalnie 500 znaków.')})

    class Meta:
        model = English
        fields = ('english', 'polish', 'sentence', 'rating')


class ContactForm(forms.ModelForm):
    name = forms.CharField(label='Twoje imię', widget=forms.TextInput(attrs={'class': 'w3-input w3-border', 'placeholder': _('pole wymagane')}))
    email = forms.EmailField(label='Twój adres e-mail', widget=forms.EmailInput(attrs={'class': 'w3-input w3-border', 'placeholder': _('pole wymagane')}))
    content = forms.CharField(
        label='Twoja wiadomość',
        widget=forms.Textarea(attrs={
            'class': 'w3-input w3-border',
            'rows': '5',
            'placeholder': _('pole wymagane')
        }))
    cc_myself = forms.BooleanField(label=_('Czy wysłać kopię wiadomości do Ciebie?'), widget=forms.CheckboxInput(attrs={'class': 'w3-check', 'checked': 'checked'}), required=False)

    class Meta:
        model = Contact
        fields = ('name', 'email', 'content', 'cc_myself')


class SearchForm(forms.Form):
    searched_text = forms.CharField(max_length=100)

    def clean_search_text(self):
        searched_text = self.cleaned_data['searched_text']
        searched_text = searched_text.strip().lower()
        searched_text = re.sub(r'[\s]{2,}', ' ', searched_text)
        return searched_text

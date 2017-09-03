from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import password_validation, get_user_model
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class SigninForm(forms.Form):
    _attributes = {
        'class': 'w3-input w3-border',
        'placeholder': _('pole wymagane'),
    }
    username = forms.CharField(widget=forms.TextInput(attrs=_attributes), label=_('Nazwa użytkownika'))
    password = forms.CharField(widget=forms.PasswordInput(attrs=_attributes), label=_('Hasło'))


class SetPasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': _("Hasła nie są takie same."),
    }
    new_password1 = forms.CharField(
        label=_("Nowe hasło"),
        widget=forms.PasswordInput(attrs={'placeholder': _('pole wymagane')}),
    )
    new_password2 = forms.CharField(
        label=_("Nowe hasło - potwierdź"),
        widget=forms.PasswordInput(attrs={'placeholder': _('pole wymagane')}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(SetPasswordForm):
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': _("Niepoprawne stare hasło."),
    })
    old_password = forms.CharField(
        label=_("stare hasło"),
        widget=forms.PasswordInput(attrs={'placeholder': _('pole wymagane')}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password


class SignupForm(forms.ModelForm):
    _attributes = {
        'class': 'w3-input w3-border',
        'placeholder': _('pole wymagane'),
    }
    error_messages = {
        'email_exists': _('Użytkownik z takim adresem e-mail już istnieje.'),
        'password_mismatch': _("Hasła nie są takie same."),
    }

    username = forms.CharField(widget=forms.TextInput(attrs=_attributes), label=_('Nazwa użytkownika'))
    email = forms.EmailField(widget=forms.EmailInput(attrs=_attributes), label=_('Adres e-mail'))
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs=_attributes), label=_('Hasło'))
    password2 = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs=_attributes), label=_('Hasło - potwierdź'))

    class Meta:
        model = User
        fields = ('username', 'email')

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def clean_email(self):
        email = self.cleaned_data['email']
        email = email.lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                self.error_messages['email_exists'],
                code='email_exists'
            )
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, domain_override=None,
             subject_template_name='authentication/signup_subject.txt',
             email_template_name='authentication/signup_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):

        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        email = email.lower()
        password = self.cleaned_data['password2']

        user = User()
        user.username = username
        user.email = email
        user.is_active = False
        user.is_superuser = False
        user.is_staff = False
        user.set_password(password)
        user.save()

        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        context = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }
        self.send_mail(
            subject_template_name, email_template_name, context, from_email,
            user.email
        )


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='authentication/password_reset_subject.txt',
             email_template_name='authentication/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data['email']
        email = email.lower()
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                context.update(extra_email_context)
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                user.email, html_email_template_name=html_email_template_name,
            )

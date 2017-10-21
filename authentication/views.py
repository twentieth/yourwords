from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import SignupForm, SigninForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
import re
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.debug import sensitive_post_parameters
from accounts.models import Profile
from django.core.mail import send_mail
from administration.models import Log


@csrf_exempt
@never_cache
def signin(request):
    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, _('Nastąpiło poprawne zalogowanie użytkownika'))
                    Log.apply(user, 1)
                    return redirect(request.POST.get('next', '/'))
                else:
                    messages.info(request, _('Twoje konto użytkownika nie jest aktywne. Skontaktuj się z administratorem strony.'))
            else:
                messages.warning(request, _('Wpisane dane są niepoprawne. Spróbuj jeszcze raz.'))
    else:
        form = SigninForm()
    context = {
        'title': _('Logowanie'),
        'form': form,
    }
    return render(request, 'authentication/signin.html', context)


@csrf_exempt
@never_cache
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': 'twentiethsite@linux.pl',
                'email_template_name': 'authentication/signup_email.html',
                'subject_template_name': 'authentication/signup_subject.txt',
                'request': request,
            }
            form.save(**opts)
            message_text = _('Na podany adres e-mail wysłaliśmy link aktywacyjny do Twojego konta. Jeśli nie otrzymasz wiadomości, sprawdź folder spam w swojej skrzynce.')
            messages.info(request, message_text)
            return redirect('authentication:signup_done')
    else:
        form = SignupForm()
    context = {
        'title': _('Rejestracja'),
        'form': form,
    }
    return render(request,'authentication/signup.html', context)


@never_cache
def logout_page(request):
    Log.apply(request.user, 2)
    logout(request)
    messages.info(request, _('Nastąpiło poprawne wylogowanie użytkownika.'))
    return redirect('yourwords:index')

@never_cache
@csrf_protect
@login_required(login_url='/authentication/signin/')
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.info(request, _('Twoje hasło zostało zmienione'))
            return redirect('yourwords:index')
    else:
        form = PasswordChangeForm(user=request.user)
    context = {
        'title': _('Nowe hasło do konta'),
        'form': form,
    }
    return render(request, 'authentication/password_change.html', context)


@never_cache
@csrf_protect
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': 'twentiethsite@linux.pl',
                'email_template_name': 'authentication/password_reset_email.html',
                'subject_template_name': 'authentication/password_reset_subject.txt',
                'request': request,
                'html_email_template_name': None,
                'extra_email_context': None,
            }
            form.save(**opts)
            message_text = _('Na podany adres e-mail wysłaliśmy instrukcję zresetowania Twojego hasła. Jeśli podany adres istnieje w naszej bazie danych, wiadomość powinna dotrzeć lada moment. Jeśli jej nie otrzymasz, sprawdź folder spam w swojej skrzynce.')
            messages.info(request, message_text)
            return redirect('authentication:password_reset_done')
    else:
        form = PasswordResetForm()
        context ={
            'title': _('Reset hasła do konta'),
            'form': form,
        }
    return render(request, 'authentication/password_reset_form.html', context)


def password_reset_done(request):
    context = {
        'title': _('Hasło zostało wysłane'),
    }
    return render(request, 'authentication/password_reset_done.html', context)


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    user_model = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = user_model._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        title = _('Wpisz nowe hasło')
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.info(request,  _('Twoje hasło zostało zmienione.'))
                return redirect('authentication:signin')
        else:
            form = SetPasswordForm(user)
    else:
        validlink = False
        form = None
        title = _('Resetowanie hasła nieudane')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    return render(request, 'authentication/password_reset_confirm.html', context)


@never_cache
def signup_done(request):
    return render(request, 'authentication/signup_done.html', {'title': _('Verification e-mail sent')})


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def signup_confirm(request, uidb64=None, token=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    user_model = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.info(request, _('Twoje konto zostało aktywowane.'))
        subject = 'TWOJESLOWKA.ONLINE' + ' - new user has registered'
        content = '''
                    Informacja o nowozarejestrowanym użytkowniku:
                    <br>''' + user.username
        send_mail(subject, '', 'twentiethsite@linux.pl', ['twentiethsite@linux.pl', 'nacoipoco@gmail.com'], fail_silently=True, html_message=content)
        return redirect('authentication:signin')
    else:
        title = _('Aktywacja nowego konta nieudana')
        messages.info(request, _('Przepraszamy, aktywacja Twojego konta nie przebiegła pomyślnie. Spróbuj później.'))
        context = {
            'title': title
        }
    return render(request, 'authentication/signup_confirm.html', context)
from random import randint
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import English
from .models import Listing
from common.helpers import user_has_option, set_pagination
from .forms import AddRecordForm, ContactForm, SearchForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.cache import cache
from yourwords.my_classes.draw_factory import DrawFactory
from common.emailer import Email
from common.helpers import safe_string
from django.core.exceptions import ObjectDoesNotExist


@csrf_exempt
def index(request):
    collection_manager = DrawFactory.get_collection_manager(request)
    record_list = collection_manager.get_collection()
    record_count = len(record_list)
    message_text = collection_manager.get_message()

    if not record_count:
        message_text = _(
            'Brak słówek spełniających wybrane kryteria. Spróbuj jeszcze raz. A może jesteś nowym użytkownikiem? Uzupełnij swoją własną bazę słówek!')
        messages.info(request, message_text)
        return redirect('yourwords:repeat', kind='write')

    messages.info(request, message_text, extra_tags='safe')
    records_to_json = {
        'record_count': record_count,
        'record_list': record_list
    }
    context = {
        'title': _('Strona domowa - losowanie'),
        'records_data': records_to_json
    }
    return render(request, 'yourwords/index.html', context)


def wordlist(request, kind=''):
    if kind == '' or kind == 'descending':
        ordering = '-created_at'
        message_text = _('Lista słówek w kolejności wg daty wprowadzenia malejąco.')
    elif kind == 'random':
        ordering = '?'
        message_text = _('Lista słówek w kolejności losowej.')
    else:
        ordering = '?'
        message_text = _('Lista słówek w kolejności losowej.')
    record_list = English.users.where_user(request.user).order_by(ordering)
    record_count = record_list.count()
    if record_count == 0:
        message_text = _('Brak słówek w bazie danych.')
    else:
        record_list = set_pagination(request, record_list, 15)

    messages.info(request, message_text, extra_tags='safe')

    context = {
        'title': _('Lista słówek'),
        'record_list': record_list,
    }
    return render(request, 'yourwords/wordlist.html', context)


@csrf_exempt
def search(request):
    context = {}
    if request.method == 'POST':
        if 'searched_text' in request.session:
            del request.session['searched_text']
        form = SearchForm(request.POST)
        if not form.is_valid():
            for message in form.errors['searched_text']:
                messages.warning(request, message)
                return render(request, 'yourwords/wordlist.html', {})
        searched_text = form.cleaned_data['searched_text']
        request.session['searched_text'] = searched_text
        if 'searched_text' not in request.session:
            messages.warning(request, _('Nie podano frazy wyszukiwania.'))
            return render(request, 'yourwords/wordlist.html', {})
        if user_has_option(request.user, 'extended_searching'):
            searched_text = request.session.get('searched_text')
            where_clause = '(polish LIKE "%%' + searched_text.replace(' ', '%%" OR polish LIKE "%%') + '%%"'
            where_clause += ' OR english LIKE "%%' + searched_text.replace(' ', '%%" OR english LIKE "%%') + '%%"'
            where_clause += ' OR sentence LIKE "%%' + searched_text.replace(' ', '%%" OR sentence LIKE "%%') + '%%")'
            where_clause += ' AND user_id = ' + str(request.user.id)
            where_clause += ' ORDER BY created_at DESC'
            query = 'SELECT id, polish, english, sentence from yourwords_english WHERE ' + where_clause
            record_list = list(English.objects.raw(query))
            record_count = len(record_list)
        elif user_has_option(request.user, 'only_full_words_searching'):
            record_list = English.users.where_user(request.user).filter(Q(polish__iregex=r"[[:<:]]{}[[:>:]]".format(searched_text)) | Q(english__iregex=r"[[:<:]]{}[[:>:]]".format(searched_text)) | Q(sentence__iregex=r"[[:<:]]{}[[:>:]]".format(searched_text)))
            record_count = record_list.count()
        else:
            record_list = English.users.where_user(request.user).filter(Q(polish__icontains=searched_text) | Q(english__icontains=searched_text) | Q(sentence__icontains=searched_text))
            record_count = record_list.count()
        if record_count == 0:
            messages.info(request, _('Nie znaleziono rekordów dla frazy') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + searched_text + '</span>', extra_tags='safe')
            return render(request, 'yourwords/wordlist.html', {})
        else:
            messages.info(request, _('Wyniki wyszukiwania dla frazy') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + searched_text + '</span> ' + _('Liczba znalezionych rekordów') + ': <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(record_count) + '</span>', extra_tags='safe')
            cache.set('record_list', record_list, None)
    context['record_list'] = set_pagination(request, cache.get('record_list'), 10)
    context['title'] = _('Wyniki wyszukiwania')
    return render(request, 'yourwords/wordlist.html', context)


@login_required()
@csrf_exempt
def add(request):
    context = {}
    request.session['current_url'] = 'yourwords:add'
    if request.method == 'POST':
        if request.is_ajax():
            form = AddRecordForm(request.POST)
            response_data = {}
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                instance.save()
                response_data['clean_form'] = 1
                response_data['records_count'] = English.users.where_user(request.user).count()
            else:
                response_data['clean_form'] = 0
                response_data['errors'] = form.errors.as_json()
            return JsonResponse(response_data)
    else:
        form = AddRecordForm()
    context['title'] = _('Dodaj słówko')
    context['form'] = form
    return render(request, 'yourwords/add.html', context)


@login_required()
@csrf_exempt
def edit(request, record_id):
    context = {}
    record = get_object_or_404(English, id=record_id)
    if not record.user == request.user:
        messages.warning(request, _('Nie masz uprawnień do żądanej strony.'))
        return redirect('yourwords:index')
    if request.method == 'POST':
        form = AddRecordForm(request.POST, instance=record)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.rating = request.POST.get('rating')
            instance.updated_at = timezone.now()
            instance.save()
            message_text = _('Wybrany rekord został zedytowany.')
            messages.success(request, message_text)
        return redirect('yourwords:edit', record_id=record.id)
    else:
        form = AddRecordForm(instance=record)
        context['title'] = _('Edytuj słówko')
        context['edit'] = True
        context['rating'] = record.rating
        context['form'] = form
        context['id'] = record.id
        return render(request, 'yourwords/add.html', context)


@login_required()
@csrf_exempt
@require_http_methods(['POST'])
def delete(request):
    if request.method == 'POST':
        if 'delete_record' in request.POST:
            record = get_object_or_404(English, id=int(request.POST.get('delete_record')))
            if not record.user == request.user:
                messages.warning(request, _('Nie masz uprawnień do żądanej strony.'))
                return redirect('yourwords:index')
            deleted = record.delete()
            if deleted:
                messages.success(request, _('Wybrany rekord został usunięty.'))
                return redirect('yourwords:index')
            else:
                messages.success(request, _('Przepraszamy, wystąpił błąd. Wybrany rekord nie został usunięty. Spróbuj później.'))
                return redirect('yourwords:edit', record_id=record.id)


@require_http_methods(['POST'])
@csrf_exempt
@login_required()
def ajax_edit_rating(request):
    if request.is_ajax():
        response_data = {}
        try:
            instance = English.users.where_user(request.user).get(id=request.POST.get('id'))
            instance.rating = request.POST.get('rating')
            instance.updated_at = timezone.now()
            instance.save()
            response_data['success'] = 1
        except ObjectDoesNotExist:
            response_data['success'] = 0
        return JsonResponse(response_data)


@csrf_exempt
def repeat(request, kind='read'):
    if request.method == 'POST':
        collection_manager = DrawFactory.get_collection_manager(request)
        record_list = collection_manager.get_collection()
        record_count = len(record_list)
        message_text = collection_manager.get_message()

        if not record_count:
            message_text = _(
                'Brak słówek spełniających wybrane kryteria. Spróbuj jeszcze raz. A może jesteś nowym użytkownikiem? Uzupełnij swoją własną bazę słówek!'
            )
            messages.info(request, message_text)
            return redirect('yourwords:repeat', kind='write')

        messages.info(request, message_text, extra_tags='safe')
        records_to_json = {
            'record_count': record_count,
            'record_list': record_list
        }
        context = {'records_data': records_to_json}
        if kind == 'read':
            return render(request, 'yourwords/index.html', context)
        else:
            return render(request, 'yourwords/repeat_writing.html', context)
    context = {
        'title': _('Ustaw zakres powtórki'),
        'kind': kind
    }
    return render(request, 'yourwords/repeat.html', context)


@csrf_exempt
def contact(request):
    context = {}
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            content = form.cleaned_data['content']
            cc_myself = form.cleaned_data['cc_myself']

            emailObject = Email()
            emailObject.set_sender('twojeslowka.online')
            subject = 'twojeslowka.online - ' + _(
                'wiadomość od Użytkownika')
            if User.objects.filter(email=email).exists():
                is_registered = True
            else:
                is_registered = False
            emailObject.set_subject(subject)
            email_context = {
                'name': name,
                'email': email,
                'subject': subject,
                'content': safe_string(content),
                'is_registered': is_registered,
            }
            emailObject.set_template('yourwords/emails/contact.html',
                                     email_context)
            recipients = ['twentiethsite@linux.pl']
            if cc_myself:
                recipients.append(email)
            emailObject.set_recipients(recipients)
            email_send = emailObject.send()
            if email_send == True:
                form.save()
                message_text = _('Dziękuję, wiadomość została wysłana.')
                messages.info(request, message_text)
            else:
                message_text = _('Wystąpił błąd - wiadomość w tej chwili nie może zostać wysłana.')
                messages.error(request, message_text)

            return redirect('yourwords:contact')
    else:
        form = ContactForm()
    context['title']= _('Napisz do nas')
    context['form'] = form
    return render(request, 'yourwords/contact.html', context)


@login_required()
def listings(request):
    listings_queryset = Listing.users.where_user(request.user).order_by('-created_at')
    context = {
        'listings': listings_queryset
    }
    return render(request, 'yourwords/loads/listings.html', context)


def about(request):
    context = {
        'title': _('O aplikacji')
    }
    return render(request, 'yourwords/about.html', context)


def cookies(request):
    context = {
        'title': _('Polityka cookies')
    }
    return render(request, 'yourwords/cookies.html', context)

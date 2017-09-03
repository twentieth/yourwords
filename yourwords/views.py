from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import English
from .models import Listing
from .services import user_has_option, set_pagination, queryset_to_json_like
from .forms import AddRecordForm, ContactForm, SearchForm
import datetime, json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.cache import cache


@csrf_exempt
def index(request):
    if not request.method == 'POST' or request.POST.get('days_before') == '-1' or request.POST.get('number_words') == '-1' or 'repeat-checked' not in request.POST or 'main_repeat' not in request.POST:
        if 'rating' in request.POST and request.POST.get('rating') != '0':
            rating = request.POST.get('rating')
            if rating == '1':
                rating_word = 'Łatwy'
            elif rating == '2':
                rating_word = 'Średni'
            elif rating == '3':
                rating_word = 'Trudny'
            record_ids = English.users.where_user(request.user).filter(rating=rating).values_list('id', flat=True)
            record_count = len(record_ids)
            message_text = _('Losowanie spośród wszystkich słówek o poziomie trudności') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + rating_word + '</span> Słówek: <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(record_count) + '</span>'
        else:
            record_ids = English.users.where_user(request.user).values_list('id', flat=True)
            record_count = len(record_ids)
            message_text = None
    if request.method == 'POST' and ('main_repeat' in request.POST or 'main_repeat_manually' in request.POST):
        main_repeat = request.POST.get('main_repeat')
        if main_repeat == '1':
            message_text = _('Losowanie spośród słówek wprowadzonych w ciągu ostatniego dnia')
        elif main_repeat == '7':
            message_text = _('Losowanie spośród słówek wprowadzonych') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">1 ' + ' ' + _('tydzień temu') + '</span>'
        elif main_repeat == '30':
            message_text = _('Losowanie spośród słówek wprowadzonych') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">1 ' + ' ' + _('miesiąc temu') + '</span>'
        elif main_repeat == '90':
            message_text = _('Losowanie spośród słówek wprowadzonych') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">3 ' + ' ' + _('miesiące temu') + '</span>'
        elif main_repeat == '180':
            message_text = _('Losowanie spośród słówek wprowadzonych') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">6 ' + ' ' + _('miesięcy temu') + '</span>'
        elif main_repeat == '365':
            message_text = _('Losowanie spośród słówek wprowadzonych') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round"> ' + _('rok temu') + '</span>'
        else:
            main_repeat = request.POST.get('main_repeat_manually')
            message_text = _('Losowanie spośród słówek wprowadzonych') + '<span class="w3-tag w3-black w3-border w3-border-light-grey w3-round"> ' + main_repeat + ' ' + _('dni temu') + '</span>'
        i = int(main_repeat) - 1
        i_plus = int(main_repeat) + 1
        record_ids = English.users.where_user(request.user).filter(created_at__gte=timezone.now()-datetime.timedelta(days=i_plus), created_at__lte=timezone.now()-datetime.timedelta(days=i)).values_list('id', flat=True)
        record_count = len(record_ids)
        message_text += _(' Słówek') + ': <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(record_count) + '</span>'
    if request.method == 'POST' and request.POST.get('days_before') != '-1' and 'days_before' in request.POST:
        days_before = int(request.POST.get('days_before'))
        message_text = _('Losowanie spośród słówek wprowadzonych w okresie ostatnich') + '<span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(days_before) + '</span> ' + _('dni') + '.'
        record_ids = English.users.where_user(request.user).filter(created_at__gte=timezone.now()-datetime.timedelta(days=days_before)).values_list('id', flat=True)
        record_count = len(record_ids)
        message_text += ' ' + _('Słówek') + ': <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(record_count) + '</span>'
    if request.method == 'POST' and request.POST.get('number_words') != '-1' and 'number_words' in request.POST:
        number_words = int(request.POST.get('number_words'))
        rating = request.POST.get('rating')
        if rating == '0' or rating =='1':
            rating_word = _('Łatwy')
        if rating == '2':
            rating_word = _('Średni')
        if rating == '3':
            rating_word = _('Trudny')
        record_ids = English.users.where_user(request.user).values_list('id', flat=True)
        record_count = len(record_ids)
        if number_words >= record_count:
            if rating == '0':
                record_ids = English.users.where_user(request.user).values_list('id', flat=True)
                record_count = len(record_ids)
                message_text = _('Losowanie spośród słówek w liczbie') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(number_words) + '</span>'
            else:
                record_ids = English.users.where_user(request.user).filter(rating=rating).values_list('id', flat=True)
                record_count = len(record_ids)
                message_text = _('Losowanie spośród słówek o poziomie trudności') + '<span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + rating_word + '</span> ' + _('Słówek') + ': <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(len(record_ids)) + '</span>'
        else:
            if rating == '0':
                record_ids = English.users.where_user(request.user).values_list('id', flat=True).order_by('?')[:number_words]
                record_count = len(record_ids)
                message_text = _('Losowanie spośród słówek w liczbie') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(number_words) + '</span>'
            else:
                record_ids = English.users.where_user(request.user).values_list('id', flat=True).filter(rating=rating).order_by('?')[:number_words]
                record_count = len(record_ids)
                message_text = _('Losowanie spośród słówek o poziomie trudności') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + rating_word + '</span> ' + _('Słówek') + ': <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(len(record_ids)) + '</span>'

    if request.method == 'POST' and 'repeat-checked' in request.POST:
        if len(request.POST.getlist('repeat-checked')) > 0:
            record_ids = request.POST.getlist('repeat-checked')
            record_count = len(record_ids)
            message_text = _('Losowanie sposród zaznaczonych słówek w liczbie') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(record_count) + '</span>'
            if request.user.is_authenticated():
                listing = Listing()
                listing.user = request.user
                listing.listing = json.dumps(record_ids)
                listing.save()
                howMany = Listing.users.where_user(request.user).count()
                if howMany > 10:
                    Listing.users.where_user(request.user).order_by('-created_at').last().delete()

    if request.method == 'POST' and 'listing' in request.POST:
        listing = Listing.users.where_user(request.user).get(id=int(request.POST.get('listing')))
        record_ids = json.loads(listing.listing)
        record_count = len(record_ids)
        message_text = _('Losowanie spośród słówek własnej listy.') + ' ' + _('Słówek') + ': <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(record_count) + '</span>'

    if record_count > 0:
        record_list = English.users.where_user(request.user).filter(id__in=list(record_ids))
        records_to_json = {
            'record_count': record_count,
            'record_list': queryset_to_json_like(record_list)
        }

        context = {
            'records_data': records_to_json
        }
        if message_text:
            messages.info(request, message_text, extra_tags='safe')
    else:
        messages.info(request, _('Brak słówek spełniających wybrane kryteria. Spróbuj jeszcze raz. A może jesteś nowym użytkownikiem? Uzupełnij swoją własną bazę słówek!'))
        return redirect('yourwords:set_repeat')

    return render(request, 'yourwords/index.html', context)


def wordlist(request, kind = ''):
    if kind == '' or kind == 'descending':
        ordering = '-created_at'
        message_text = _('Lista słówek w kolejności wg daty wprowadzenia malejąco.')
    elif kind == 'random':
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
        if user_has_option(request.user, 'extended_searching'):
            if 'searched_text' not in request.session:
                messages.warning(request, _('Nie podano frazy wyszukiwania.'))
                return render(request, 'yourwords/wordlist.html', {})
            searched_text = request.session.get('searched_text')
            where_clause = '(polish LIKE "%%' + searched_text.replace(' ', '%%" OR polish LIKE "%%') + '%%"'
            where_clause += ' OR english LIKE "%%' + searched_text.replace(' ', '%%" OR english LIKE "%%') + '%%"'
            where_clause += ' OR sentence LIKE "%%' + searched_text.replace(' ', '%%" OR sentence LIKE "%%') + '%%")'
            where_clause += ' AND user_id = ' + str(request.user.id)
            where_clause += ' ORDER BY created_at DESC'
            query = 'SELECT id, polish, english, sentence from yourwords_english WHERE ' + where_clause
            record_list = list(English.objects.raw(query))
            record_count = len(record_list)
        else:
            record_list = English.users.where_user(request.user).filter(Q(polish__icontains=searched_text) | Q(english__icontains=searched_text) | Q(sentence__icontains=searched_text))
            record_count = len(record_list)
        if record_count == 0:
            messages.info(request, _('Nie znaleziono rekordów dla frazy') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + searched_text + '</span>', extra_tags='safe')
            return render(request, 'yourwords/wordlist.html', {})
        else:
            messages.info(request, _('Wyniki wyszukiwania dla frazy') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + searched_text + '</span> ' + _('Liczba znalezionych rekordów') + ': <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(record_count) + '</span>', extra_tags='safe')
            cache.set('record_list', record_list, None)
    context['record_list'] = set_pagination(request, cache.get('record_list'), 10)
    context['title'] = _('Wyniki wyszukiwania')
    return render(request, 'yourwords/wordlist.html', context)


@login_required(login_url='/authentication/signin/')
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


@login_required(login_url='/authentication/signin/')
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


@login_required(login_url='/authentication/signin/')
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
@login_required(login_url='/authentication/signin/')
def ajax_edit_rating(request):
    if request.is_ajax():
        response_data = {}
        instance = English.users.where_user(request.user).get(id=request.POST.get('id'))
        instance.rating = request.POST.get('rating')
        instance.updated_at = timezone.now()
        instance.save()
        response_data['success'] = 1
        return JsonResponse(response_data)


@csrf_exempt
def set_repeat(request):
    context = {
        'title': _('Ustaw zakres powtórki'),
    }
    return render(request, 'yourwords/set_repeat.html', context)


@csrf_exempt
def contact(request):
    context = {}
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['your_name']
            email = form.cleaned_data['your_email']
            message = form.cleaned_data['your_message']
            cc_myself = form.cleaned_data['cc_myself']

            subject = _('[[yourwords]] Wiadomość od użytkownika ') + name
            if User.objects.filter(email=email).exists():
                subject = '#' + subject

            mail_content = '''
Wiadomość od: ''' + name + '''
E-mail: ''' + email + '''

"
''' + message + '''
"
'''

            recipients = ['twentiethsite@linux.pl']
            if cc_myself:
                recipients.append(email)

            ifTrue = send_mail(subject, mail_content, 'twentiethsite@linux.pl', recipients)
            if ifTrue:
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


@login_required(login_url='/authentication/signin/')
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
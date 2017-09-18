from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from .models import Option
from .forms import OptionForm
from django.contrib import messages


@login_required(login_url='/authentication/signin/')
@csrf_exempt
def option_settings(request):
    context = {
        'title': _('Ustawienia użytkownika')
    }
    option = Option.objects.get(user=request.user)
    if request.method == 'POST':
        if request.is_ajax():
            response_data = {}
            form = OptionForm(request.POST, instance=option)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                if instance.only_full_words_searching:
                    instance.extended_searching = False
                instance.save()
                response_data['success'] = 1
            else:
                response_data['success'] = 0
            return JsonResponse(response_data)
        else:
            form = OptionForm(request.POST, instance=option)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                if instance.only_full_words_searching:
                    instance.extended_searching = False
                instance.save()
                messages.info(request, _('Ustawienia zostały zapisane.'))
            else:
                messages.error(request, _('Przepraszamy, wystąpił błąd. Ustawienia nie zostały zapisane.'))
            return redirect('yourwords:index')
    else:
        form = OptionForm(instance=option)
        context['form'] = form
    return render(request, 'accounts/loads/option_settings.html', context)


def language(request):
    context = {
        'title': _('Zmień język')
    }
    return render(request, 'accounts/loads/language.html', context)


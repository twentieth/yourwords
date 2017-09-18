from random import shuffle
import json
import datetime
from django.utils.translation import ugettext as _
from django.utils import timezone
from yourwords.models import English
from yourwords.models import Listing
from common.helpers import queryset_to_json_like


class DrawFactory:
    __DAYS_BEFORE = 'days_before'
    __DAYS_AGO = 'main_repeat'
    __NUMBER_WORDS = 'number_words'
    __REPEAT_CHECKED = 'repeat-checked'

    @classmethod
    def get_collection_manager(cls, request):
        if request.method == 'GET':
            return AllWordsManager(request)
        elif request.method == 'POST':
            if cls.__DAYS_AGO in request.POST:
                return DaysAgoManager(request)
            elif cls.__DAYS_BEFORE in request.POST:
                return DaysBeforeManager(request)
            elif cls.__NUMBER_WORDS in request.POST:
                return NumberWordsManager(request)
            elif cls.__REPEAT_CHECKED in request.POST:
                return RepeatCheckedManager(request)
            else:
                return AllWordsManager(request)


class CollectionManager:
    def __init__(self, request):
        self._request = request
        self._records_ids = []
        self._count = 0
        self._message = ''

    def get_collection(self):
        records_list = English.users.where_user(self._request.user).filter(id__in=self._records_ids)
        return queryset_to_json_like(records_list)

    def get_count(self):
        return self._count

    def get_message(self):
        return self._message


class DaysBeforeManager(CollectionManager):
    def __init__(self, request):
        CollectionManager.__init__(self, request)
        self.__days_before = int(self._request.POST.get('days_before'))
        if self.__days_before == -1:
            self._records_ids = English.users.where_user(self._request.user).order_by('?').values_list('id', flat=True)
            self._count = len(self._records_ids)
        else:
            self._records_ids = English.users.where_user(self._request.user).filter(created_at__gte=timezone.now() - datetime.timedelta(days=self.__days_before)).order_by('?').values_list('id', flat=True)
            self._count = len(self._records_ids)
            self._message = 'Losowanie spośród słówek wprowadzonych w okresie ostatnich ' + \
                            '<span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + \
                            str(self.__days_before) + '</span> dni.' + \
                            ' Słówek: <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + \
                            str(self._count) + '</span>'
        

class DaysAgoManager(CollectionManager):
    def __init__(self, request):
        CollectionManager.__init__(self, request)
        if 'main_repeat_manually' not in self._request.POST:
            self.__days_ago = int(self._request.POST.get('main_repeat'))
        elif 'main_repeat_manually' in self._request.POST:
            self.__days_ago = int(self._request.POST.get('main_repeat_manually'))
        i = self.__days_ago - 1
        i_plus = self.__days_ago + 1
        self._records_ids = English.users.where_user(request.user).filter(created_at__gte=timezone.now() - datetime.timedelta(days=i_plus), created_at__lte=timezone.now() - datetime.timedelta(days=i)).order_by('?').values_list('id', flat=True)
        if self.__days_ago == 1:
            self._message = _('Losowanie spośród słówek wprowadzonych w ciągu ostatniego dnia')
        elif self.__days_ago == 7:
            self._message = _('Losowanie spośród słówek wprowadzonych') + \
                ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">1 ' + \
                ' ' + _('tydzień temu') + \
                '</span>'
        elif self.__days_ago == 30:
            self._message = _('Losowanie spośród słówek wprowadzonych') + \
                ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">1 ' + \
                ' ' + _('miesiąc temu') + '</span>'
        elif self.__days_ago == 90:
            self._message = _('Losowanie spośród słówek wprowadzonych') + \
                ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">3 ' + \
                ' ' + _('miesiące temu') + '</span>'
        elif self.__days_ago == 180:
            self._message = _('Losowanie spośród słówek wprowadzonych') + \
                ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">6 ' + \
                ' ' + _('miesięcy temu') + '</span>'
        elif self.__days_ago == 365:
            self._message = _('Losowanie spośród słówek wprowadzonych') + \
                ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round"> ' + \
                _('rok temu') + '</span>'
        else:
            self._message = _('Losowanie spośród słówek wprowadzonych') + \
                '<span class="w3-tag w3-black w3-border w3-border-light-grey w3-round"> ' + \
                str(self.__days_ago) + ' ' + _('dni temu') + '</span>'
        self._count = len(self._records_ids)
        self._message += ' Słówek: <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + \
                         str(self._count) + '</span>'


class NumberWordsManager(CollectionManager):
    __RATING_NONE = 0
    __RATING_EASY = 1
    __RATING_MEDIUM = 2
    __RATING_DIFFICULT = 3
    __NUMBER_WORDS_ALL = -1

    def __init__(self, request):
        CollectionManager.__init__(self, request)
        self.__number_words = int(self._request.POST.get('number_words'))
        self.__rating = int(self._request.POST.get('rating'))
        self._count = len(self._records_ids)
        if self.__rating == self.__RATING_EASY:
            rating_word = _('Łatwy')
        elif self.__rating == self.__RATING_MEDIUM:
            rating_word = _('Średni')
        elif self.__rating == self.__RATING_DIFFICULT:
            rating_word = _('Trudny')
        else:
            rating_word = ''
        if self.__rating == self.__RATING_NONE and self.__number_words == self.__NUMBER_WORDS_ALL:
            self._records_ids = English.users.where_user(self._request.user).order_by('?').values_list('id', flat = True)
            self._count = len(self._records_ids)
        elif self.__rating == self.__RATING_NONE and self.__number_words != self.__NUMBER_WORDS_ALL:
            self._records_ids = English.users.where_user(self._request.user).order_by('?').values_list('id', flat=True)[:self.__number_words]
            self._count = len(self._records_ids)
            self._message = _('Losowanie spośród słówek w liczbie') + \
                ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + \
                str(self.__number_words) + '</span>'
        elif self.__rating != self.__RATING_NONE and self.__number_words == self.__NUMBER_WORDS_ALL:
            self._records_ids = English.users.where_user(self._request.user).filter(rating=self.__rating).order_by('?').values_list('id', flat=True)
            self._count = len(self._records_ids)
            self._message = _('Losowanie spośród słówek o poziomie trudności') + ' ' + '<span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + \
                rating_word + '</span> ' + \
                _('Słówek') + ': <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + \
                str(self._count) + '</span>'
        else:
            # self.__rating != self.__RATING_NONE and self.__number_words != self.__NUMBER_WORDS_ALL
            self._records_ids = English.users.where_user(self._request.user).filter(rating=self.__rating).order_by('?').values_list('id', flat=True)[:self.__number_words]
            self._count = len(self._records_ids)
            self._message = _('Losowanie spośród słówek o poziomie trudności') + ' ' + '<span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + \
                rating_word + '</span> ' + \
                _('Słówek') + ': <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + \
                str(self._count) + '</span>'


class RepeatCheckedManager(CollectionManager):
    def __init__(self, request):
        CollectionManager.__init__(self, request)
        self.__repeat_checked = self._request.POST.getlist('repeat-checked')
        if len(self.__repeat_checked) > 0:
            self._records_ids = self.__repeat_checked
            self._count = len(self._records_ids)
            self._message = _('Losowanie sposród zaznaczonych słówek w liczbie') + ' <span class="w3-tag w3-black w3-border w3-border-light-grey w3-round">' + str(self._count) + '</span>'
            if self._request.user.is_authenticated():
                listing = Listing()
                listing.user = self._request.user
                listing.listing = json.dumps(self._records_ids)
                listing.save()
                how_many = Listing.users.where_user(self._request.user).count()
                if how_many > 10:
                    Listing.users.where_user(self._request.user).order_by('-created_at').last().delete()


class AllWordsManager(CollectionManager):
    def __init__(self, request):
        CollectionManager.__init__(self, request)
        self._records_ids = English.users.where_user(self._request.user).order_by('?').values_list('id', flat=True)
        self._count = len(self._records_ids)
        

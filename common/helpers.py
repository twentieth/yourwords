from random import randrange
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_current_url(request):
    return request.build_absolute_uri()


def random_record(request):
    response_data = {}
    if cache.get('record_count') is None or cache.get('record_list') is None:
        response_data['success'] = 0
    else:
        random_value = randrange(0, cache.get('record_count'))
        record_list = cache.get('record_list')
        try:
            response_data['success'] = 1
            record = record_list[random_value]
            response_data['id'] = record.id
            response_data['polish'] = record.polish
            response_data['english'] = record.english
            response_data['sentence'] = record.sentence
            response_data['rating'] = record.rating
        except ObjectDoesNotExist:
            response_data = random_record(request)
    return response_data


def user_has_option(user, option):
    if user.is_authenticated():
        if user.option.has_option(option):
            return True
        else:
            return False
    else:
        return False


def set_pagination(request, collection, n):
    paginator = Paginator(collection, int(n))
    page = request.GET.get('page')
    try:
        collection = paginator.page(page)
    except PageNotAnInteger:
        collection = paginator.page(1)
    except EmptyPage:
        collection = paginator.page(paginator.num_pages)
    return collection


def queryset_to_json_like(queryset):
    import datetime
    queryset = queryset.values()
    array = []
    for record in queryset:
        for key, value in record.items():
            if isinstance(value, datetime.datetime):
                record[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif value is None:
                record[key] = "0000-00-00 00:00:00"
        array.append(record)
    return array


def json_like_from_queryset_with_id_keys(json_like, pk='id'):
    array = {}
    for record in json_like:
        array[record[pk]] = record
    return array


def safe_string(string):
    from django.utils.safestring import mark_safe
    return mark_safe(string.strip().replace("\n", "<br>\n"))

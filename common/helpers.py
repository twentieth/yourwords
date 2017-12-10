def get_current_url(request):
    return request.build_absolute_uri()


def user_has_option(user, option):
    if user.is_authenticated():
        if user.option.has_option(option):
            return True
        else:
            return False
    else:
        return False


def set_pagination(request, collection, n):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(collection, int(n))
    page = request.GET.get('page')
    try:
        collection = paginator.page(page)
    except PageNotAnInteger:
        collection = paginator.page(1)
    except EmptyPage:
        collection = paginator.page(paginator.num_pages)
    return collection


def queryset_to_dict(queryset):
    import datetime
    queryset = queryset.values()
    array = []
    for record in queryset:
        for key, value in record.items():
            if isinstance(value, datetime.datetime):
                record[key] = str(value)
        array.append(record)
    return array


def queryset_to_dict_with_id_keys(queryset, pk='id'):
    import datetime
    queryset = queryset.values()
    d = {}
    for record in queryset:
        for key, value in record.items():
            if isinstance(value, datetime.datetime):
                record[key] = str(value)
        d[record[pk]] = record
    return d


def queryset_to_dict_serializer_version(queryset, pk='id'):
    import json
    from django.core import serializers
    serialized_data = serializers.serialize('json', queryset)
    deserialized_data = json.loads(serialized_data)
    array = []
    for record in deserialized_data:
        record['fields'][pk] = record['pk']
        array.append(record['fields'])
    return array


def queryset_to_dict_with_id_keys_serializer_version(queryset, pk='id'):
    import json
    from django.core import serializers
    serialized_data = serializers.serialize('json', queryset)
    deserialized_data = json.loads(serialized_data)
    d = {}
    for record in deserialized_data:
        record[pk] = record['pk']
        d[record['pk']] = record['fields']
    return d


def safe_string(string):
    from django.utils.safestring import mark_safe
    return mark_safe(string.strip().replace("\n", "<br>\n"))

from django.conf.urls import url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns


app_name = 'api'
urlpatterns = [
    url(r'^words/$', views.EnglishList.as_view(), name='word_list'),
    url(r'^words/(?P<pk>[0-9]+)/$',
        views.EnglishDetail.as_view(), name='word_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

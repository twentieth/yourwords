from django.conf.urls import url
from . import views

app_name = 'yourwords'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^list/(?P<kind>(descending|random))/$', views.wordlist, name='wordlist'),
    url(r'^list/$', views.wordlist, name='wordlist'),
    url(r'^listings/$', views.listings, name='listings'),
    url(r'^add/$', views.add, name='add'),
    url(r'^delete/$', views.delete, name='delete'),
    url(r'^edit/(?P<record_id>[0-9]+)/$', views.edit, name='edit'),
    url(r'^ajax_edit_rating/$', views.ajax_edit_rating, name='ajax_edit_rating'),
    url(r'^repeat/(?P<kind>(read|write))/$', views.repeat, name='repeat'),
    url(r'^repeat/$', views.repeat, name='repeat'),
    url(r'^search/$', views.search, name='search'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^about/$', views.about, name='about'),
    url(r'^cookies/$', views.cookies, name='cookies'),
]

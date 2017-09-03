from django.conf.urls import url
from . import views

app_name = 'authentication'
urlpatterns = [
	url(r'^signin/$', views.signin, name='signin'),
	url(r'^logout_page/$', views.logout_page, name='logout_page'),
	url(r'^password_change/$', views.password_change, name='password_change'),
	url(r'^password_reset/$', views.password_reset, name='password_reset'),
	url(r'^password_reset/done/$', views.password_reset_done, name='password_reset_done'),
	url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.password_reset_confirm, name='password_reset_confirm'),
	url(r'^signup/$', views.signup, name='signup'),
	url(r'^signup/done/$', views.signup_done, name='signup_done'),
	url(r'^signup_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.signup_confirm, name='signup_confirm'),
]
 

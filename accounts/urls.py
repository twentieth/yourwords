from django.conf.urls import url
from accounts import views

app_name = 'accounts'
urlpatterns = [
    url(r'^settings/$', views.option_settings, name='option_settings'),
    url(r'^language/$', views.language, name='language'),
]
 

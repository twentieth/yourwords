"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns


urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^yourwords/', include('yourwords.urls')),
    url(r'^', include('yourwords.urls')),
    url(r'^testing/', include('testing.urls')),
    url(r'^authentication/', include('authentication.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^social-auth/', include('social_django.urls', namespace='social')),
    url(r'^rosetta/', include('rosetta.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
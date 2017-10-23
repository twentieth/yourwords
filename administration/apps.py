from django.apps import AppConfig
from django.utils.translation import ugettext, ugettext_lazy as _


class AdministrationConfig(AppConfig):
    name = 'administration'
    verbose_name = _('Administration')

    def ready(self):
        import administration.signals



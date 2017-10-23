from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Log


@receiver(user_logged_in)
def user_has_logged_in(sender, user, request, **kwargs):
    Log.objects.create(user=user, action='1',
                       ip=request.META.get('REMOTE_ADDR'))

@receiver(user_logged_out)
def user_has_logged_out(sender, user, request, **kwargs):
    Log.objects.create(user=user, action='2',
                       ip=request.META.get('REMOTE_ADDR'))

@receiver(post_save, sender=User)
def user_has_registered(sender, instance, created, **kwargs):
    if created:
        Log.objects.create(user=instance, action='3')


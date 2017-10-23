from django.db import models
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    photo = models.ImageField(upload_to='users/%Y%m%d', blank=True, null=True)

    def is_socialuser(self):
        try:
            UserSocialAuth.objects.get(user=self.user)
            return True
        except ObjectDoesNotExist:
            return False

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Option(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    extended_searching = models.BooleanField(default=False)
    only_full_words_searching = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_option(sender, instance, created, **kwargs):
        if created:
            Option.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_option(sender, instance, **kwargs):
        instance.option.save()

    def has_option(self, option):
        if hasattr(self, option):
            exists = getattr(self, option)
            if exists:
                return True
            else:
                return False
        else:
            return False

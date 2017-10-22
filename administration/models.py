from django.db import models
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


class Log(models.Model):
    ACTION_CHOICES = (
        ('1', 'The user has logged in.'),
        ('2', 'The user has logged out.'),
    )
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    action = models.CharField(max_length=255, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} | {} | {}'.format(self.user.username, self.action, self.created_at)

    @classmethod
    def apply(cls, user, action):
        # logModel = cls(user=user, action=action)
        # try:
        #     logModel.save()
        #     return True
        # except IntegrityError:
        #     return False
        # except ValueError:
        #     return False
        pass

    @receiver(user_logged_in)
    def user_has_been_logged_in(sender, user, request, **kwargs):
        logModel = Log(user=user, action='1')
        try:
            logModel.save()
            return True
        except IntegrityError:
            return False
        except ValueError:
            return False

    @receiver(user_logged_out)
    def user_has_been_logged_out(sender, user, request, **kwargs):
        logModel = Log(user=user, action='2')
        try:
            logModel.save()
            return True
        except IntegrityError:
            return False
        except ValueError:
            return False

from django.db import models


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
        logModel = cls(user=user, action=action)
        try:
            logModel.save()
            return True
        except IntegrityError:
            return False
        except ValueError:
            return False

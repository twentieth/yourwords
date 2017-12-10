from django.db import models
from django.utils import timezone


class UserManager(models.Manager):
    def where_user(self, user):
        if user.is_authenticated():
            user_id = user.id
        else:
            user_id = 1
        return super(UserManager, self).get_queryset().filter(user_id=user_id)


class English(models.Model):
    objects = models.Manager()
    users = UserManager()
    RATING_CHOICES = (
        ('1', 'easy'),
        ('2', 'medium'),
        ('3', 'difficult'),
    )
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=1)
    polish = models.CharField(max_length=100, default='')
    english = models.CharField(max_length=100, default='')
    sentence = models.TextField(max_length=500, blank=True, null=True)
    rating = models.CharField(
        max_length=1, default=RATING_CHOICES[0][0], choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=False, null=True)

    def clean(self):
        self.polish = self.polish.strip().upper()
        self.english = self.english.strip().lower()
        if self.created_at is not None:
            self.updated_at = timezone.now()
        if not self.rating:
            self.rating = '1'

    def save(self, *args, **kwargs):
        self.clean()
        super(English, self).save(*args, **kwargs)

    def __str__(self):
        return '{} | {}'.format(self.english, self.polish)


class Listing(models.Model):
    objects = models.Manager()
    users = UserManager()
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100, blank=True, null=True)
    listing = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=False, null=True)

    def __str__(self):
        return self.user.username + ' ' + str(self.created_at)


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    cc_myself = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

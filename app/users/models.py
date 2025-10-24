import string, random

from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone


class UserBase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userbase')
    recovery_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class UserWarnings(models.Model):
    user = models.ForeignKey('UserBase', on_delete=models.CASCADE)
    warning_type = models.ForeignKey('WarningType', on_delete=models.SET_NULL, null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)


class WarningType(models.Model):
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.description

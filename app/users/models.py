import string, random

from django.db import models

from django.contrib.auth.models import User


class UserBase(User):
    recovery_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def generate_recovery_code(self):
        code = string.ascii_letters + string.digits
        while True:
            new_code = ''.join(random.choice(code) for _ in range(10))
            if not UserBase.objects.filter(recovery_code=new_code).exists():
                self.recovery_code = new_code
                self.save()
                return new_code


class UserWarnings(models.Model):
    user = models.ForeignKey('UserBase', on_delete=models.CASCADE)
    warning_type = models.ForeignKey('WarningType', on_delete=models.SET_NULL, null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)


class WarningType(models.Model):
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.description

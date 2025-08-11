from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class UserBase(User):

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
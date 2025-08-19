import random
import string

from django.db import models
from django.contrib.auth.models import User

from app.users.models import UserBase


class School(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schools', null=True, blank=True)
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='school_photos/', null=True, blank=True)
    logo = models.ImageField(upload_to='school_logo/', null=True, blank=True)
    general_description = models.TextField(null=True, blank=True)
    income_description = models.TextField(null=True, blank=True)
    recovery_code = models.CharField(max_length=10, unique=True, null=True, blank=True)


    def __str__(self):
        return self.name

    @property
    def average_valoration(self):
        comentarios = self.school_comments.all()
        if comentarios.exists():
            return round(sum(c.score for c in comentarios) / comentarios.count(), 2)

        return None

    def generate_recovery_code(self):
        code = string.ascii_letters + string.digits
        while True:
            new_code = ''.join(random.choice(code) for _ in range(10))
            if not School.objects.filter(recovery_code=new_code).exists():
                self.recovery_code = new_code
                self.save()
                return new_code


class Career(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='careers')
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    duration = models.CharField(max_length=50, null=True, blank=True)  # e.g., "4 years", "2 years"
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} - {self.school.name}'


class BaseComment(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Comment(BaseComment):
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='school_comments', null=True, blank=True)
    score = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'{self.user} {self.description[:10]}...'


class Reply(BaseComment):
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='replies')
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='school_replies')
    parent = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'{self.user} {self.description[:10]}...'


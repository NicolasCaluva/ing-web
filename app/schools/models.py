from django.db import models
from django.contrib.auth.models import User

from app.users.models import UserBase


class School(models.Model):
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='schools', null=True, blank=True)
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='school_photos/', null=True, blank=True)
    logo = models.ImageField(upload_to='school_logo/', null=True, blank=True)
    general_description = models.TextField(null=True, blank=True)
    income_description = models.TextField(null=True, blank=True)
    career_description = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.name

    @property
    def average_valoration(self):
        comentarios = self.school_comments.all()
        if comentarios.exists():
            return round(sum(c.score for c in comentarios) / comentarios.count(), 2)

        return None


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
        return f'{self.user.username[:10]} {self.description[:10]}...'


class Reply(BaseComment):
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='replies')
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='school_replies')
    parent = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'{self.user.username[:10]} {self.description[:10]}...'


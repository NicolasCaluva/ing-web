from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    school_user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255, null=False, blank=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='school_photos/', null=True, blank=True)
    logo = models.ImageField(upload_to='school_logo/', null=True, blank=True)
    general_description = models.TextField(null=False, blank=False)
    income_description = models.TextField(null=False, blank=False)
    career_description = models.TextField(null=False, blank=False)

    def __str__(self):
        return f'{self.name} - {self.school_user.email}'

    @property
    def average_valoration(self):
        comments = self.comments.all()
        if comments.exists():
            return round(sum(c.valoration for c in comments) / comments.count(), 2)
        return None


class Comment(models.Model):
    user = models.ForeignKey('users.UserBase', on_delete=models.CASCADE, related_name='comments')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='comments')
    valoration = models.IntegerField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    response_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='responses')
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.school.name}: {self.description[:20]}...'
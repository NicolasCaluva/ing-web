from django.db import models

from app.users.models import UserBase


class BaseComment(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Comment(BaseComment):
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='school_comments', null=True,
                               blank=True)
    score = models.PositiveSmallIntegerField(default=0)
    is_reported = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} {self.description[:10]}...'


class Reply(BaseComment):
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='replies')
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='school_replies')
    parent = models.ForeignKey('comments.Comment', on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'{self.user} {self.description[:10]}...'

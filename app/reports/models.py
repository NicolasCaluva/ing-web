# reports/models.py
from django.db import models

class Report(models.Model):
    user = models.ForeignKey('users.UserBase', on_delete=models.CASCADE)
    comment = models.ForeignKey('comments.Comment', on_delete=models.CASCADE)
    reason = models.TextField(null=False, blank=False)
    is_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'comment'], name='uniq_user_comment_report')
        ]

    def __str__(self):
        return f'Report by {self.user} on comment {self.comment.id}'

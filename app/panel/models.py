from django.db import models

# Create your models here.

class Report(models.Model):
    user = models.ForeignKey('users.UserBase', on_delete=models.CASCADE)
    comment = models.ForeignKey('schools.Comment', on_delete=models.CASCADE)
    reason = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f'Report by {self.user} on comment {self.comment.id}'

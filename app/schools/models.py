from django.db import models

# Create your models here.
class School(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(null=False, blank=False)
    password = models.CharField(max_length=128, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='school_photos/', null=True, blank=True)
    logo = models.ImageField(upload_to='school_logo/', null=True, blank=True)
    general_description = models.TextField(null=False, blank=False)
    income_description = models.TextField(null=False, blank=False)
    career_description = models.TextField(null=False, blank=False)

    def __str__(self):
        return f'{self.name} - {self.email}'

    @property
    def average_valoration(self):
        comentarios = self.comments.all()
        if comentarios.exists():
            return round(sum(c.valoration for c in comentarios) / comentarios.count(), 2)
        return None
class Comment(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='comments')
    valoration = models.IntegerField(null=False, blank=False)
    comment = models.TextField(null=False, blank=False)
    isresponse = models.BooleanField(default=False)
    response_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='responses')
    user = models.ForeignKey('users.UserBase', on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.school.name}: {self.comment[:20]}...'
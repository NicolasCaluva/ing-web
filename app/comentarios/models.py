from django.db import models


# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=100)


class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BaseComment(models.Model):
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    text = models.TextField()
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Comment(BaseComment):
    score = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.author.name[:10] + self.text[:10] + '...'


class Reply(BaseComment):
    parent = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return self.author.name[:10] + self.text[:10] + '...'
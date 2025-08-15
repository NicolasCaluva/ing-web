from django import forms
from .models import Reply, Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['description', 'score']

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['description']
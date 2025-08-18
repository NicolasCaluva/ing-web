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

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['description', 'score', 'user']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu comentario aquí...'}),
            'score': forms.Select(choices=[(i, i) for i in range(1, 5)], attrs={'class': 'form-select'})
        }

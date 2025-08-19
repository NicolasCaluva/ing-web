from django import forms
from .models import Reply, Comment

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['description']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['description', 'score']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu comentario aquí...'}),
            'score': forms.HiddenInput(),  # El valor lo envías desde los radio buttons en el template
        }
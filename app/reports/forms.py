from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['comment', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Explica la razón del reporte...'}),
        }
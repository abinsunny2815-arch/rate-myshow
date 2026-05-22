"""
Forms for ratings app.
"""
from django import forms
from apps.ratings.models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating/editing reviews."""
    
    class Meta:
        model = Review
        fields = ('title_review', 'content', 'contains_spoilers')
        widgets = {
            'title_review': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review Title (optional)',
                'maxlength': '300'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your review here...',
                'rows': 8
            }),
            'contains_spoilers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

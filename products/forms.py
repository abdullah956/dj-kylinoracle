from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['reviewer_name', 'reviewer_email', 'rating', 'message']
        widgets = {
            'rating': forms.RadioSelect,
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('reviewer_email')
        if not email:
            raise forms.ValidationError('Email is required.')
        return email

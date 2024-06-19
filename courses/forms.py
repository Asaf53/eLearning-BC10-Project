from django import forms
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Review

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["stars", "description"]
        # fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'stars': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 1, 'class': 'form-control'}),
        }
        validators = [
            MinValueValidator(1),
            MaxValueValidator(5)
        ]

    def clean_stars(self):
        stars = self.cleaned_data['stars']
        if stars < 1 or stars > 5:
            raise forms.ValidationError("Stars must be between 1 and 5.")
        return stars

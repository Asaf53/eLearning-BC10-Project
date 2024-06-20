from django import forms
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Review
from .models import Course
from .models import Media
from django.forms import formset_factory

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
    
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['category', 'name', 'description', 'price', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class VideoForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['name', 'courses_video']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'courses_video': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CourseSearchForm(forms.Form):
    search_query = forms.CharField(label='Search Courses', max_length=100)

VideoFormSet = forms.inlineformset_factory(Course, Media, form=VideoForm, extra=1, can_delete=True)

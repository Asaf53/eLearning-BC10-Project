from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from django.db.models import Avg


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    
class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField(default=0.0)
    image = models.ImageField(null=True, blank=True, default='noimage.jpg', upload_to="courses/")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_reviews(self):
        if self.review_set.all() is not None:
            return self.review_set.all()
        return []

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ForeignKey(Course, on_delete=models.CASCADE)
    total = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class Media(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    courses_video = models.FileField(upload_to='courses_video/')


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

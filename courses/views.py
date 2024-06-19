from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ReviewForm
from .models import *


def index(request):
    courses_list = Course.objects.all().order_by("-id")
    categories = Category.objects.all()
    page_num = request.GET.get("page", 1)

    paginator = Paginator(courses_list, 9)

    try:
        courses = paginator.page(page_num)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    context = {"courses": courses, "categories": categories}
    return render(request, "home.html", context)


def category_courses(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    courses_list = Course.objects.filter(category=category)
    categories = Category.objects.all()
    page_num = request.GET.get("page", 1)

    paginator = Paginator(courses_list, 9)

    try:
        courses = paginator.page(page_num)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    context = {"courses": courses, "categories": categories}
    return render(request, "category.html", context)


def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    context = {"course": course, "review_form": ReviewForm}
    return render(request, "course_detail.html", context)


@login_required
@permission_required("reviews.add_review")
def create_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = Review(
                student=User.objects.filter(id=request.POST["student_id"]).first(),
                course=Course.objects.filter(id=request.POST["course_id"]).first(),
                stars=request.POST["stars"],
                description=request.POST["description"],
            )
            review.save()
            return redirect("course_detail", request.POST["course_id"])

    return redirect("course_detail", request.POST["course_id"])


@login_required
def dashboard(request):
    context = {"enrollemts": Enrollment.objects.filter(student_id=request.user.id)}
    return render(request, "dashboard.html", context)


@login_required
def become_instructor(request):
    user = request.user

    if user.groups.filter(name="instructor").exists():
        messages.info(request, "You are already a instructor.")
        return redirect("dashboard")

    if user.groups.filter(name="student").exists():
        user.groups.remove(Group.objects.filter(name="student").first())
        user.groups.add(Group.objects.filter(name="instructor").first())
        messages.success(request, "You have become a instructor.")

    return redirect("dashboard")


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("index")

        form = UserCreationForm()

        context = {"form": form}

        return render(request, "registration/register.html", context)

    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            user.groups.add(Group.objects.filter(name="student").first())
            login(request, user)
            return redirect("index")
        return render(request, "home.html", {"form": form})


def signout(request):
    logout(request)
    return redirect("login")

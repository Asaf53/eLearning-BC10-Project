from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CourseForm, VideoFormSet, CourseSearchForm, ReviewForm
from .models import *
from cart.cart import Cart

# home page
def index(request):
    courses_list = Course.objects.all().order_by("-id")
    categories = Category.objects.all()

    search_query = request.GET.get('q')
    if search_query:
        courses_list = courses_list.filter(name__icontains=search_query)
    
    page_num = request.GET.get("page", 1)

    paginator = Paginator(courses_list, 9)

    try:
        courses = paginator.page(page_num)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)


    search_form = CourseSearchForm()

    enrolled_courses = []
    if request.user.is_authenticated:
        enrolled_courses = Enrollment.objects.filter(student=request.user).values_list('courses', flat=True)


    context = {"courses": courses, "categories": categories, "search_form": search_form, "enrolled_courses": enrolled_courses}
    return render(request, "home.html", context)

# category page
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

    context = {"courses": courses, "categories": categories, 'category':category}
    return render(request, "category.html", context)

# course detail
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    videos = Media.objects.filter(course=course)
    is_enrolled = False
    if request.user.is_authenticated:
        if Enrollment.objects.filter(student=request.user, courses=course).exists():
            is_enrolled = True
            messages.info(request, "You are already enrolled in this course.")
    context = {"course": course, "review_form": ReviewForm, "is_enrolled": is_enrolled, "videos": videos}
    return render(request, "course_detail.html", context)

# add review
@login_required
@user_passes_test(lambda u: u.groups.filter(name='instructor').exists())
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

# user dashboard
@login_required
def dashboard(request):
    user = request.user
    if user.groups.filter(name='student').exists():
        context = {"enrollments": Enrollment.objects.filter(student_id=request.user.id)}
    else:
        context = {"courses": Course.objects.filter(instructor_id=request.user.id)}
    return render(request, "dashboard.html", context)

# change group permission
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

# auth
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

#shopping cart 
@login_required
def cart_add(request, id):
    cart = Cart(request)
    course = Course.objects.get(id=id)
    cart.add(product=course)
    return redirect("index")


@login_required
def item_clear(request, id):
    cart = Cart(request)
    course = Course.objects.get(id=id)
    cart.remove(course)
    return redirect("index")

@login_required
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required
def cart_detail(request):
    return render(request, 'cart/cart_detail.html')

# upload course
@login_required
@permission_required("courses.add_course")
def upload_course(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES)
        video_formset = VideoFormSet(request.POST, request.FILES)

        if course_form.is_valid() and video_formset.is_valid():
            course = course_form.save(commit=False)
            course.instructor = request.user
            course.save()
            videos = video_formset.save(commit=False)
            for video in videos:
                video.course = course
                video.save()
            return redirect('course_detail', course_id=course.id)
    else:
        course_form = CourseForm()
        video_formset = VideoFormSet()

    return render(request, 'upload_course.html', {
        'course_form': course_form,
        'video_formset': video_formset,
    })

# update course
@login_required
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course_form = CourseForm(request.POST, request.FILES, instance=course)
        video_formset = VideoFormSet(request.POST, request.FILES, instance=course)

        if course_form.is_valid() and video_formset.is_valid():
            course_form.save()
            video_formset.save()
            messages.success(request, "Course updated successfuly")
            return redirect('course_detail', course_id=course.pk)
    else:
        course_form = CourseForm(instance=course)
        video_formset = VideoFormSet(instance=course)
    
    return render(request, 'update_course.html', {
        'course_form': course_form,
        'video_formset': video_formset,
    })
# delete course
@login_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return redirect('dashboard')

# checkout
@login_required
def checkout(request):
    cart = request.session.get("cart", {}).items()

    total = 0
    for id, item in cart:
        total += float(item['price'])

    enrollment = Enrollment(student=request.user, total=total)
    enrollment.save()

    for id, item in cart:
        enrollment.courses.add(Course.objects.filter(name=item['name']).first())

    c = Cart(request)
    c.clear()

    return redirect('dashboard')
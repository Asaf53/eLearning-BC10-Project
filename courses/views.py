from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from .models import *


def index(request):
    context = {
        'courses' : Course.objects.all().order_by('-id')[0:4]
    }
    return render(request, "index.html", context)    

def dashboard(request):
    pass


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
            user.groups.add(Group.objects.filter(name="customer").first())
            login(request, user)
            return redirect("index")
        return render(request, "home.html", {"form": form})


def signout(request):
    logout(request)
    return redirect("login")

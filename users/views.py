from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages


def index(request):
    return HttpResponse("Hi")


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('index')  # Замените 'home' на имя вашего URL
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                messages.success(request, f'Hello <b>{user.username}</b>! You have been logged in')
                return redirect('index')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('index')  # Замените 'home' на имя вашего URL



from django.shortcuts import render , redirect, HttpResponse
from django.contrib.auth import authenticate, login as auth_login , logout 
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile


# Create your views here.


def register_user(request):
  if request.method == 'POST':
      username = request.POST.get("username")
      email = request.POST.get("email")
      password = request.POST.get("password")
      is_superuser = request.POST.get("is_superuser", 'off') == 'on'
      is_staff = request.POST.get("is_staff", 'off') == 'on'
      is_active = request.POST.get("is_active", 'off') == 'on'
      energy_type = request.POST.get("energy_type")
      user = User(username=username, email = email, is_superuser=is_superuser,is_staff = is_staff, is_active=is_active)
      user.set_password(password)
      user.save()     
      UserProfile.objects.create(user=user, energy_type=energy_type)  
      return HttpResponse("User registered successfully!")
  else:
    energy_choices = UserProfile._meta.get_field('energy_type').choices 
    return render(request, 'signup.html', context={"energy_choices":energy_choices})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('/dashboard') 
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('/')
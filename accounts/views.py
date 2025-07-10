from django.shortcuts import render , redirect, HttpResponse
from django.contrib.auth import authenticate, login as auth_login , logout 
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile  ,EnergyType
from django.contrib.auth.decorators import login_required


@login_required
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        is_superuser = request.POST.get("is_superuser", 'off') == 'on'
        is_staff = request.POST.get("is_staff", 'off') == 'on'
        is_active = request.POST.get("is_active", 'off') == 'on'
        selected_ids = request.POST.getlist("energy_types")
        user = User(
            username=username,
            email=email,
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_active=is_active
        )
        user.set_password(password)
        user.save()
        # Create profile first without energy_types
        profile = UserProfile.objects.create(user=user)
        # Then set the ManyToManyField
        profile.energy_types.set(selected_ids)
        return HttpResponse("User registered successfully!")
    else:
        energy_choices = EnergyType.objects.all()
        return render(request, 'signup.html', context={"energy_choices": energy_choices})


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
    return redirect('login')

from django.core.paginator import Paginator
from django.contrib.auth.models import User
from accounts.models import UserProfile

@login_required
def user_list(request):
    username = request.GET.get('username', '')
    energy_type = request.GET.get('energy_type', '')
    status = request.GET.get('status', '')
    users = User.objects.all().select_related('userprofile')
    if username:
        users = users.filter(username__icontains=username) | users.filter(email__icontains=username)

    if energy_type:
        users = users.filter(userprofile__energy_type=energy_type)

    if status:
        users = users.filter(is_active=(status == 'active'))

    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'user_list.html', {
        'users': page_obj,
        'username': username,
        'energy_type': energy_type,
        'status': status,
        'page_obj': page_obj,
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from accounts.models import UserProfile

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')  # Assuming you named the URL
    return HttpResponse("Invalid request.")

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.is_active = 'is_active' in request.POST
        user.is_staff = 'is_staff' in request.POST
        user.is_superuser = 'is_superuser' in request.POST
        new_password = request.POST.get("password")
        if new_password:
            user.set_password(new_password)

        user.save()
         # ✅ Correct handling of ManyToManyField
        selected_energy_ids = request.POST.getlist("energy_types")
        profile.energy_types.set(selected_energy_ids)
        profile.save()
        messages.success(request, "User updated successfully.")
        return redirect('user_list')
    # GET request
    energy_choices = EnergyType.objects.all()
    selected_energy_ids = profile.energy_types.values_list('id', flat=True)
    return render(request, 'edit_user.html', {
        'user_obj': user,
        'energy_choices': energy_choices,
        'selected_energy_ids': selected_energy_ids
    })

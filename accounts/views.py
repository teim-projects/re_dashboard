from django.shortcuts import render , redirect, HttpResponse
from django.contrib.auth import authenticate, login as auth_login , logout 
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile  ,EnergyType
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.shortcuts import redirect

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

        profile = UserProfile.objects.create(user=user)
        profile.energy_types.set(selected_ids)

        messages.success(request, "User registered successfully!")
        return redirect('user_list')  # or wherever you want to show the modal

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

from django.db.models import Q

@login_required
def user_list(request):
    username = request.GET.get('username', '')
    energy_type = request.GET.get('energy_type', '')
    status = request.GET.get('status', '')

    users = User.objects.all().select_related('userprofile').distinct()

    if username:
        users = users.filter(Q(username__icontains=username) | Q(email__icontains=username))

    if energy_type:
        users = users.filter(userprofile__energy_types__name__iexact=energy_type)

    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'user_list.html', {
        'users': page_obj,
        'page_obj': page_obj,
        'username': username,
        'energy_type': energy_type,
        'status': status,
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


from django.shortcuts import render, redirect
from .models import EnergyType
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def add_energy_type(request):
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            # Handle deletion
            delete_id = request.POST.get('delete_id')
            EnergyType.objects.filter(id=delete_id).delete()
            messages.success(request, "Energy type deleted successfully!")
            return redirect('register_user')  # 👈 redirect to register_user

        # Handle add
        name = request.POST.get('name')
        if name:
            name = name.strip()
            obj, created = EnergyType.objects.get_or_create(name=name)
            if created:
                messages.success(request, "Energy type added successfully!")
            else:
                messages.warning(request, "Energy type already exists.")
            return redirect('register_user')  # 👈 redirect to register_user
        else:
            messages.error(request, "Please enter a valid name.")

    energy_types = EnergyType.objects.all()
    return render(request, 'add_energy_type.html', {'energy_types': energy_types})

import pandas as pd
from django.db import connection
from .models import Provider
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import os
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, IntegrityError
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from .models import Provider

import os
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, IntegrityError
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from .models import Provider

@login_required
def add_provider_with_structure(request):
    if request.method == 'POST':
        # ✅ Delete request
        if 'delete_id' in request.POST:
            delete_id = request.POST.get('delete_id')
            try:
                provider = Provider.objects.get(id=delete_id)
                table_name = f"{provider.name.lower().replace(' ', '_')}_data"

                # Drop the dynamic table
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

                provider.delete()
                messages.success(request, f"Provider and table '{table_name}' deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error while deleting provider: {str(e)}")
            return redirect("add_provider")

        # ✅ Add provider and create table
        provider_name = request.POST.get("provider_name", "").strip()
        structure_file = request.FILES.get("structure_file")

        if not provider_name or not structure_file:
            messages.error(request, "Provider name and file are required.")
            return redirect("add_provider")

        try:
            provider = Provider.objects.create(name=provider_name.lower())
        except IntegrityError:
            messages.error(request, f"Provider '{provider_name}' already exists.")
            return redirect("add_provider")

        # Save the uploaded file temporarily
        fs = FileSystemStorage()
        filename = fs.save(structure_file.name, structure_file)
        file_path = fs.path(filename)

        try:
            df = pd.read_csv(file_path) if filename.endswith(".csv") else pd.read_excel(file_path)

            table_name = f"{provider_name.lower().replace(' ', '_')}_data"
            columns = df.columns

            # 🧩 Convert headers into valid SQL field names and append system columns
            column_defs = [f"`{col.strip().replace(' ', '_').lower()}` TEXT" for col in columns]
            column_defs.append("`energy_type` TEXT")
            column_defs.append("`uploaded_by` TEXT")


            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                {", ".join(column_defs)}
            );
            """

            with connection.cursor() as cursor:
                cursor.execute(create_table_sql)

            messages.success(request, f"Provider '{provider_name}' and table '{table_name}' created successfully.")

        except Exception as e:
            messages.error(request, f"Error creating table: {str(e)}")

        finally:
            fs.delete(filename)

        return redirect("add_provider")

    # GET request: show form and provider list
    providers = Provider.objects.all()
    return render(request, 'add_Provider.html', {'providers': providers})

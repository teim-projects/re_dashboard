from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required


def index_page(request):
  return render(request, 'index.html')


@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser:
        return render(request, 'home.html')  # Admin dashboard
    else:
        return render(request, 'customer_home.html')  # Regular user dashboard
    

from django.contrib.auth.models import User
from accounts.models import EnergyType

@login_required
def upload_files(request):
    energy_types = EnergyType.objects.all()

    # Show all non-superuser users (including normal and staff users)
    staff_users = User.objects.filter(is_superuser=False)

    return render(request, 'upload_files.html', {
        'energy_types': energy_types,
        'staff_users': staff_users,
    })


@login_required
def modify_data(request):
  return render(request,'modify_data.html')

@login_required
def manage_user(request):
   return render(request, 'manageUsers.html')

@login_required
def client_info(request):
   return render(request, 'client_info.html')
 
 
 

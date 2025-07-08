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

@login_required
def upload_files(request):
    return render(request,'upload_files.html')

@login_required
def modify_data(request):
  return render(request,'modify_data.html')

@login_required
def manage_user(request):
   return render(request, 'manageUsers.html')

@login_required
def client_info(request):
   return render(request, 'client_info.html')
 
 
 
from django.contrib.auth.models import User
from django.shortcuts import render
from accounts.models import UserProfile

def user_list(request):
    users = User.objects.all().select_related('userprofile')  # Efficient query
    return render(request, 'user_list.html', {'users': users}) 
  
  
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from accounts.models import UserProfile

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')  # Assuming you named the URL
    return HttpResponse("Invalid request.")

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.is_active = 'is_active' in request.POST
        user.is_staff = 'is_staff' in request.POST
        user.is_superuser = 'is_superuser' in request.POST
        user.save()

        profile = user.userprofile
        profile.energy_type = request.POST.get("energy_type")
        profile.save()

        return redirect('user_list')
    
    energy_choices = UserProfile._meta.get_field('energy_type').choices
    return render(request, 'edit_user.html', {
        'user_obj': user,
        'energy_choices': energy_choices
    })
  
  
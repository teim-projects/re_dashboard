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
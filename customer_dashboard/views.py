from django.shortcuts import render

def dashboard(request):
  return render(request, 'customer_home.html')
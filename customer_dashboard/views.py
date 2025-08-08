from django.shortcuts import render

def wind_dashboard(request):
    return render(request, 'customer_home.html')  # Wind Dashboard

def solar_dashboard(request):
    return render(request, 'solar_dashboard.html')  # Solar Dashboard

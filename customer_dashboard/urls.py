from django.urls import path
from .views import *

urlpatterns = [
    path('wind_dashboard', wind_dashboard, name="wind_dashboard"),  # Wind
    path('solar/', solar_dashboard, name="solar_dashboard"),  # Solar
]

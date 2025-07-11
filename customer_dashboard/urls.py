from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name="customer_dashboard"),  # Wind
    path('solar/', solar_dashboard, name="solar_dashboard"),  # Solar
]

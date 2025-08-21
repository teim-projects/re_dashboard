from django.urls import path
from solardashboard import views

urlpatterns = [
    path('solar/', views.solar_dashboard, name="solar_dashboard"),  # Solar
    path('solar_summary1', views.solar_summary1, name="solar_summary1"),  # Solar
    path('installation_summary2/', views.installation_summary2, name="installation_summary2"),  # Wind Installation Summary
]

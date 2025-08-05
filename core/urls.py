from django.urls import path
from .views import *
from django.urls import include

urlpatterns = [
  path('', index_page, name="index"),
  path('dashboard/', dashboard, name='dashboard'),
  path('upload-files/', upload_files, name='upload_files'),
  path('modify-data/', modify_data, name="modify_data"),
  path('manage-users/', manage_user, name='manage_users'),
  path('client-info/',client_info, name="client_info"),
  path('accounts/',include('accounts.urls')),
  path('upload-installation-summary/',upload_installation_summary, name='upload_installation_summary'),
  path('upload-installation-data/', upload_installation_data, name='upload_installation_data'),
    path('download-template/',download_template, name='download_template'),




]

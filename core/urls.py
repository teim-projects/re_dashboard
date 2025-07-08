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
  path('user-list/', user_list, name='user_list'),
  path('edit-user/<int:user_id>/', edit_user, name='edit_user'),
  path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
  path('accounts/',include('accounts.urls'))
  
]

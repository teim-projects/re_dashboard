from django.urls import path
from .views import *



urlpatterns = [
  path('register-user/', register_user, name="register_user"),
  path('login/', login_view, name="login"),
  path('logout/', logout_view, name='logout'),
    path('user-list/', user_list, name='user_list'),
  path('edit-user/<int:user_id>/', edit_user, name='edit_user'),
  path('delete-user/<int:user_id>/', delete_user, name='delete_user')
  
  
]

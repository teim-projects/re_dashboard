from django.urls import path
from .views import *

urlpatterns = [
  path('register-user/', register_user, name="register_user"),
  path('login/', login_view, name="login"),
  path('logout/', logout_view, name='logout'),
  
]

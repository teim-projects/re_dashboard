from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  energy_type = models.CharField(max_length=50, choices=[
    ("Wind","Wind"),
    ("Solar","Solar")
  ] )

  def __str__(self):
    return self.user.username + "-" + self.energy_type

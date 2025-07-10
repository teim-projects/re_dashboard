from django.db import models
from django.contrib.auth.models import User


class EnergyType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  energy_types = models.ManyToManyField(EnergyType) 

  def __str__(self):
    return self.user.username + " - " + ", ".join([et.name for et in self.energy_types.all()])


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EnergyType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    energy_types = models.ManyToManyField(EnergyType)
    password_updated_at = models.DateTimeField(default=timezone.now)  # 🆕 Add this field

    def __str__(self):
        return self.user.username + " - " + ", ".join([et.name for et in self.energy_types.all()])

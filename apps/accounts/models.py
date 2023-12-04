from django.db import models
from .manages import CustomUserManager
from django.contrib.auth.models import AbstractUser



class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'vm_users'

    def __str__(self):
        return self.email

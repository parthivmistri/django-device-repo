from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


# Create your models here.

class User(AbstractUser):
    first_name = models.TextField('first name')
    last_name = models.TextField('last name')

    objects = UserManager()

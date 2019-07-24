from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class User(AbstractUser):
    first_name = models.TextField('first name')
    last_name = models.TextField('last name')
    otp = models.IntegerField('otp', null=True)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

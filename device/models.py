from django.db import models

from accounts.models import User

DEVICE_TYPES = (
    ('Android', 'Android'),
    ('iOS', 'iOS')
)


class Device(models.Model):
    device_name = models.CharField(max_length=200)
    IMEI_no = models.IntegerField()
    is_engaged = models.BooleanField(default=False)
    device_type = models.CharField(max_length=1, choices=DEVICE_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_device')

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.timezone import now


class CustomUser(AbstractUser):
    is_doctor = models.BooleanField(default=False)


class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Session for {self.user.username} at {self.created_at}"
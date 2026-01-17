from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model extending AbstractUser to include additional fields.
    """
    age = models.IntegerField(null=True, blank=True, help_text="User's age")
    phone_number = models.CharField(max_length=15, blank=True, help_text="Contact number")
    bio = models.TextField(blank=True, help_text="User biography")
    email = models.EmailField(unique=True, help_text="Email address")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

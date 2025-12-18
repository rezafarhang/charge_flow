from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from apps.users.consts import UserRole


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=255,
        unique=True
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )
    email_verified = models.BooleanField(
        default=False
    )
    password = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    is_admin = models.BooleanField(
        default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

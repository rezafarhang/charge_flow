from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from apps.users import consts


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
    role = models.SmallIntegerField(
        choices=[(role.value, role.name) for role in consts.UserRole],
        default=consts.UserRole.SELLER.value
    )

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin


class PhoneNumber(models.Model):
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name='phone_balance_non_negative'
            ),
        ]

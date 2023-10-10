# models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.


from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import timedelta


from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class myAccountManager(BaseUserManager):
    def create_user(self, username, email, phone_number, password=None):
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone_number, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
            phone_number=phone_number,
        )
        user.is_librarian = True  # added
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # required
    is_active = models.BooleanField(default=True)
    is_librarian = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = ["email", "phone_number"]

    objects = myAccountManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


class Books(models.Model):
    Title = models.CharField(max_length=200)
    author = models.CharField(max_length=50)
    count = models.PositiveIntegerField(default=0)
    rent_count = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class BookRequests(models.Model):
    REQUEST_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    )
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="requests")
    requested_by = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name="requested_books"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=REQUEST_STATUS_CHOICES, default="pending"
    )

    def __str__(self):
        return f"Request for {self.book.title} by {self.requested_by.username}"

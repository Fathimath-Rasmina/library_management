# models.py
from django.db import models
from datetime import timedelta
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
import random
import string


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
        user.is_librarian = True
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
        return self.Title

    def save(self, *args, **kwargs):
        is_new = self.id is None  # Check if the book is being created

        super(Books, self).save(*args, **kwargs)

        if is_new:
            for _ in range(self.count):
                serial_number = "".join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(10)
                )
                SerialNumbers.objects.create(book=self, serial_number=serial_number)


class SerialNumbers(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=10, unique=True)
    is_assigned = models.BooleanField(default=False)

    class Meta:
        unique_together = ("book", "serial_number")

    def __str__(self):
        return f" {self.book.Title} by {self.book.author}"


class BookRequests(models.Model):
    REQUEST_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    )
    _id = models.AutoField(primary_key=True, editable=False)
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="requests")
    requested_by = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name="requested_books"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=REQUEST_STATUS_CHOICES, default="pending"
    )

    def __str__(self):
        return f"Request for {self.book.Title} by {self.requested_by.username}"


class RentedBooks(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    serial_number = models.ForeignKey(SerialNumbers, on_delete=models.CASCADE)
    rented_by = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    rental_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned = models.BooleanField(default=False)
    fine = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.book.Title} by {self.book.author}, Rented by {self.rented_by.username}"

    def save(self, *args, **kwargs):
        if self.rental_date is None:
            self.rental_date = timezone.now()

        # Set the due_date to be 7 days after the rental_date
        self.due_date = self.rental_date + timedelta(days=7)
        super(RentedBooks, self).save(*args, **kwargs)

    def return_book(self):
        if not self.returned:
            self.returned = True

            # Calculate the fines
            today = timezone.now()
            overdue_days = (today - self.due_date).days

            if overdue_days > 0:
                if overdue_days <= 7:
                    fine = 5  # 5 rupees for the first 1 week
                else:
                    fine = (
                        5 + (overdue_days - 7) * 10
                    )  # 10 rupees for each day after 1 week

            else:
                fine = 0

            self.fine = fine

            # Update the associated book status and rent count
            book = self.book
            book.is_available = True
            book.rent_count -= 1

            serial_number = self.serial_number
            serial_number.is_assigned = False
            serial_number.save()

            self.save()
            book.save()

            return fine

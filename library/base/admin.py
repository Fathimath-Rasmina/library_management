from django.contrib import admin

# Register your models here.
from .models import MyUser, Books, BookRequests, SerialNumbers, RentedBooks

admin.site.register(MyUser)
admin.site.register(Books)
admin.site.register(BookRequests)
admin.site.register(SerialNumbers)
admin.site.register(RentedBooks)

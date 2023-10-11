from django.contrib import admin

# Register your models here.
from .models import MyUser, Books, BookRequests

admin.site.register(MyUser)
admin.site.register(Books)
admin.site.register(BookRequests)

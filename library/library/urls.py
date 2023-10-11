# project url file

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("base.urls.user_urls")),
    path("books/", include("base.urls.book_urls")),
]

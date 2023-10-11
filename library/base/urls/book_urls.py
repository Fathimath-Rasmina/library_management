from django.urls import path
from ..views.book_views import (
    BookListCreateView,
    BookRetrieveUpdateDeleteView,
    RequestToRentBookView,
    ManageBookRequestsView,
    ListBookRequestsView,
)

urlpatterns = [
    path("manage_books/", BookListCreateView.as_view(), name="manage_books"),
    path(
        "rent_request_list/", ManageBookRequestsView.as_view(), name="rent_request_list"
    ),
    #
    path(
        "manage_books/<int:pk>/",
        BookRetrieveUpdateDeleteView.as_view(),
        name="books_crud",
    ),
    path(
        "rent_request/<int:book_id>/",
        RequestToRentBookView.as_view(),
        name="rent_request",
    ),
    path(
        "rent_request_handle/<int:request_id>/",
        ManageBookRequestsView.as_view(),
        name="rent_request_handle",
    ),
]

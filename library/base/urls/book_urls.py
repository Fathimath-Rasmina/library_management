from django.urls import path
from ..views.book_views import (
    BookListCreateView,
    BookRetrieveUpdateDeleteView,
    RequestToRentBookView,
    ManageBookRequestsView,
    ReturnBook,
    ListRentedBooksView,
    ListSerialNumbersView,
)

urlpatterns = [
    path("manage_books/", BookListCreateView.as_view(), name="manage_books"),
    path("rented_books/", ListRentedBooksView.as_view(), name="rented_books"),
    path(
        "rent_request_list/", ManageBookRequestsView.as_view(), name="rent_request_list"
    ),
    path("serial_numbers/", ListSerialNumbersView.as_view(), name="serial_numbers"),
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
    path("return_book/<int:rented_book_id>/", ReturnBook.as_view(), name="return_book"),
]

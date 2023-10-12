# views.py
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from ..serializers import BooksSerializer, BookRequestsSerializer, RentedBookSerializers

from rest_framework import viewsets
from ..models import Books, BookRequests, RentedBooks
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsLibrarianOrReadOnly
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from ..notification import send_rental_request_notification


# * view for member creation and view member list
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]


# * view for member CRUD operations
class BookRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]


# * list book requests
class ListBookRequestsView(generics.ListAPIView):
    queryset = BookRequests.objects.all()
    serializer_class = BookRequestsSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]


# * List all rented books
class ListRentedBooksView(generics.ListAPIView):
    queryset = RentedBooks.objects.all()
    serializer_class = RentedBookSerializers
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]


# * request to rent a book , views.py
class RequestToRentBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        # Check if the user already has an active rented book
        user = request.user
        existing_rented_book = RentedBooks.objects.filter(
            rented_by=user, returned=False
        ).first()

        if existing_rented_book:
            return Response(
                {"message": "You already have an active rented book"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            book = Books.objects.get(pk=book_id)
        except Books.DoesNotExist:
            return Response(
                {"message": "Book not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if the book is available for rent
        if book.is_available:
            # Create a new BookRequest instance
            request_data = {
                "book": book_id,
                "requested_by": user.id,
                "status": "pending",  # Set the initial status to 'pending'
            }
            serializer = BookRequestsSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()
                # Notify the librarian of the new request
                send_rental_request_notification(serializer.instance)
                return Response(
                    {"message": "Request sent successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "This book is not available for rent"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# * Rent a book request handling
class ManageBookRequestsView(APIView):
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]

    def get(self, request):
        # Retrieve a list of all rent requests
        rent_requests = BookRequests.objects.all()
        serializer = BookRequestsSerializer(rent_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, request_id):
        try:
            book_request = BookRequests.objects.get(_id=request_id)
        except BookRequests.DoesNotExist:
            return Response(
                {"message": "Request not found"}, status=status.HTTP_404_NOT_FOUND
            )

        request_status = request.data.get("status")

        if request_status in ["approved", "declined"]:
            if book_request.status in ["approved", "declined"]:
                # If the book request is already approved or declined, return an error message
                return Response(
                    {
                        "message": f"Sorry, the book request is already {book_request.status}."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif request_status == "approved":
                # Check if the book is available before approving
                if book_request.book.is_available:
                    # Increment the rent count
                    book_request.book.rent_count += 1
                    book_request.book.save()

                    # Check if all books are rented, and update availability status
                    if book_request.book.count == book_request.book.rent_count:
                        book_request.book.is_available = False

                    # Create a new RentedBooks instance
                    rented_book = RentedBooks.objects.create(
                        book=book_request.book,
                        rented_by=book_request.requested_by,
                    )

                    # Update the book request status
                    book_request.status = request_status
                    book_request.save()

                    # Save the rented book instance to the database
                    rented_book.save()

                    return Response(
                        {"message": "Request approved"}, status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"message": "Book is not available"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif request_status == "declined":
                book_request.status = request_status
                book_request.save()
                return Response(
                    {"message": "Request declined"}, status=status.HTTP_200_OK
                )
        else:
            return Response(
                {"message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )


# view for returning the book
class ReturnBook(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, rented_book_id):
        try:
            rented_book = RentedBooks.objects.get(pk=rented_book_id)
        except RentedBooks.DoesNotExist:
            return Response(
                {"message": "Rented book not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not rented_book.returned:
            fine = rented_book.return_book()
            if fine > 0:
                return Response(
                    {
                        "message": f"Book returned successfully. You have overdue Fine: ₹{fine}"
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message": "Book returned successfully within duedate",
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"message": "Book is already returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

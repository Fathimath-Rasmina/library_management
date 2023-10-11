# notification.py
from django.core.mail import send_mail
from .models import MyUser


def send_rental_request_notification(book_request):
    librarian = MyUser.objects.filter(is_librarian=True).first()

    if librarian:
        subject = "New Book Rental Request"
        message = f"A new rental request has been made for the book '{book_request.book.Title}' by {book_request.requested_by.username}."
        from_email = "your@example.com"  # Replace with your email
        recipient_list = [librarian.email]

        send_mail(subject, message, from_email, recipient_list)

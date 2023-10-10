# permissions.py
from rest_framework import permissions


class IsLibrarianOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow librarians to add, update, and delete members.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow read-only access to all users
        else:
            # Only allow librarians to perform write operations
            return request.user.is_authenticated and request.user.is_librarian

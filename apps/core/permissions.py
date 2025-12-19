from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    message = 'You must be an admin to perform this action.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )

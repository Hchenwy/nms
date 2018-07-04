
from rest_framework import permissions

class IsValidUser(permissions.IsAuthenticated, permissions.BasePermission):
    """Allows access to valid user, is active and not expired"""

    def has_permission(self, request, view):
        return super(IsValidUser, self).has_permission(request, view) \
            and request.user.is_valid

class IsSuperUser(IsValidUser):
    """Allows access only to superuser"""

    def has_permission(self, request, view):
        return super(IsSuperUser, self).has_permission(request, view) \
            and request.user.is_superuser

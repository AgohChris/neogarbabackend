from rest_framework import permissions
from apps.cores.enums import RoleEnum

class EstAdministrateur(permissions.BasePermission):
    """
    Permission that only allows users with the ADMINISTRATEUR role,
    is_staff, or is_superuser to access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (
                request.user.role == RoleEnum.ADMINISTRATEUR or
                request.user.is_staff or
                request.user.is_superuser
            )
        )

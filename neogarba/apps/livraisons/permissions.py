from rest_framework import permissions

class EstLivreur(permissions.BasePermission):
    """
    Permission that only allows users with the role LIVREUR to access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'LIVREUR'
        )


class EstServeur(permissions.BasePermission):
    """
    Permission that only allows users with the role SERVEUR to access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'SERVEUR'
        )

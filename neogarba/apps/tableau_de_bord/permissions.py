from rest_framework.permissions import BasePermission


class EstAdministrateur(BasePermission):
    """
    seul l'administrateur peut acceder au tableau de bord.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMINISTRATEUR'

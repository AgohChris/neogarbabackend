from rest_framework.permissions import BasePermission

class EstVendeur(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'VENDEUR'

class LectureOuVendeur(BasePermission):
    # Tout le monde peut lire, seul le vendeur peut écrire
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.role == 'VENDEUR'
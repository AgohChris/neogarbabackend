from rest_framework.permissions import BasePermission
from apps.cores.enums import RoleEnum


class HasRole(BasePermission):
  
    required_role = None

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == self.required_role
        )

    @classmethod
    def for_role(cls, role):
        return type(f'HasRole_{role}', (cls,), {'required_role': role})
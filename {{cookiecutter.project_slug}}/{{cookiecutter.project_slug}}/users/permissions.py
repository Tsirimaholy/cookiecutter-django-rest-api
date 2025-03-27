from rest_framework.permissions import IsAdminUser

from .models import Role
from .models import User


class IsAdmin(IsAdminUser):
    def has_permission(self, request, view):
        # super model just checks for is_staff attribute
        user: User = request.user
        is_staff = super().has_permission(request, view)
        return bool(is_staff and (user.has_role(Role.ADMIN)))

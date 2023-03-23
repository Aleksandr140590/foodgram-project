from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user and request.user.is_authenticated:
            if obj.author == request.user:
                return True
            raise PermissionDenied(
                'У вас не достаточно прав для редактирования!'
            )
        return False


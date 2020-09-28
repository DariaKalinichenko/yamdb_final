from rest_framework import permissions, exceptions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            if view.kwargs['username'] == 'me' and request.user.role:
                return True
        except Exception:
            pass

        try:
            return request.user.role == 'admin'
        except Exception:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        try:
            return request.user.role == 'admin'
        except Exception:
            return False


class MethodPermissions(permissions.BasePermission):
    """
    Prohibiting the use of any method other than "delete" for working
    with categories and genres
    """
    def has_permission(self, request, view):
        if view.kwargs:
            if request.method == 'DELETE':
                return True
            raise exceptions.MethodNotAllowed(request.method)
        return True


class IsModeratorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', '') == 'moderator'

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH':
            return obj.author == request.user
        return False

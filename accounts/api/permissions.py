from rest_framework.permissions import BasePermission


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class IsOwnerOrReadOnlyOrSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return obj == request.user

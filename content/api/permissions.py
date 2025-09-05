from rest_framework.permissions import BasePermission
from content.models import Post


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


def is_owner_or_superuser(request, view):
    """
    Permission method that allows access to owner or a superuser.
    """
    user = request.user
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    pk = view.kwargs.get('pk', None)
    if pk is not None:
        try:
            obj = Post.objects.get(pk=pk)
            return obj.author == user
        except Post.DoesNotExist:
            return False


class IsSuperuser(BasePermission):
    """
    Permission class that allows access to a superuser.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_superuser


class IsOwnerOrReadOnlyOrSuperuser(BasePermission):
    """
    Permission class that allows read-only access to everyone,
    but only the object's owner or a superuser can modify it.
    """
    def has_object_permission(self, request, view, obj=None):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return obj.author == request.user
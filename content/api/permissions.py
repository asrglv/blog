from rest_framework.permissions import BasePermission
from content.models import Post


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


def is_owner_or_superuser(request, view):
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
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_superuser


class IsOwnerOrReadOnlyOrSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj=None):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return obj.author == request.user
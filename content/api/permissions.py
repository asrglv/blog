from rest_framework.permissions import BasePermission
from content.models import Post


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_superuser


class IsOwnerOrSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj=None):
        pk = view.kwargs.get('pk', None)
        if obj is None and pk is not None:
            obj = Post.objects.get(pk=pk)
        if request.user.is_authenticated:
            return (request.user.is_superuser or
                    obj is not None and obj.author == request.user)


class IsOwnerOrReadOnlyOrSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj=None):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return obj.author == request.user
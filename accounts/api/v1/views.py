from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from .serializers import (UserReadSerializer,
                          UserCreateSerializer,
                          UserUpdateSerializer,
                          ChangePasswordSerializer)
from accounts.api.permissions import IsOwnerOrReadOnlyOrSuperuser


class PaginationMixin:
    """
    Mixin for safe pagination with fallback for invalid pages.
    """
    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except NotFound:
            page = request.GET.get('page')
            request._request.GET = request._request.GET.copy()
            if not page.isdigit():
                request._request.GET['page'] = 1
            else:
                last_page = (queryset.count() - 1) // self.page_size + 1
                request._request.GET['page'] = last_page
            return super().paginate_queryset(queryset, request, view)


class UserPagination(PaginationMixin, PageNumberPagination):
    """
    Pagination class for the User model.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserModelViewSet(ModelViewSet):
    """
    API endpoint for managing users.

    Provides list, retrieve, create, update, and delete actions
    for User instances.
    """
    pagination_class = UserPagination
    permission_classes = [IsOwnerOrReadOnlyOrSuperuser]

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserReadSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return NotFound('Method not allowed')


class ChangePasswordAPIView(GenericAPIView):
    """
    API endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'detail': 'Password was changed.'})
        return Response(serializer)
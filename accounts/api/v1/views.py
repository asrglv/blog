from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from accounts.models import User
from .serializers import (UserReadSerializer,
                          UserCreateSerializer,
                          UserUpdateSerializer)
from accounts.api.permissions import IsOwnerOrReadOnlyOrSuperuser


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserModelViewSet(ModelViewSet):
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

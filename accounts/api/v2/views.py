from rest_framework import generics
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


class UserListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = UserPagination
    permission_classes = [IsOwnerOrReadOnlyOrSuperuser]

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserReadSerializer
        elif self.request.method == 'POST':
            return UserCreateSerializer
        return NotFound('Method not allowed')


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrReadOnlyOrSuperuser]

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserReadSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return NotFound('Method not allowed')
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from content.models import Post
from .serializers import PostReadSerializer, PostCreateUpdateSerializer


class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20


class PostListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = PostPagination

    def get_queryset(self):
        return Post.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostReadSerializer
        elif self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return NotFound('Method Not allowed')


class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Post.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostReadSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return NotFound('Method Not allowed')

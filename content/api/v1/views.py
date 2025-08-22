from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from content.models import Post
from .serializers import PostReadSerializer, PostCreateUpdateSerializer


class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20


class PostViewSet(ModelViewSet):
    pagination_class = PostPagination
    
    def get_queryset(self):
        return Post.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PostReadSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return NotFound("Method not allowed")

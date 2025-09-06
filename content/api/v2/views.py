from redis import StrictRedis
from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     GenericAPIView,
                                     ListAPIView)
from content.models import Post, Comment
from taggit.models import Tag
from .serializers import (PostListSerializer,
                          PostRetrieveSerializer,
                          PostCreateUpdateSerializer,
                          TagSerializer,
                          CommentReadSerializer,
                          CommentCreateSerializer,
                          CommentUpdateSerializer,
                          LikeSerializer)
from content.api.permissions import (IsSuperuser,
                                     is_owner_or_superuser,
                                     IsOwnerOrReadOnlyOrSuperuser)
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


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


class TagPagination(PaginationMixin, PageNumberPagination):
    """
    Pagination class for the Tag model.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class PostPagination(PaginationMixin, PageNumberPagination):
    """
    Pagination class for the Post model.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20


class CommentPagination(PaginationMixin, PageNumberPagination):
    """
    Pagination class for the Comment model.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class TagCreateListAPIView(ListCreateAPIView):
    """
    API endpoint for managing tags.

    Provides GET, POST methods for Tag instances.
    POST method available for users with administrator permissions.
    """
    pagination_class = TagPagination

    def get_queryset(self):
        return Tag.objects.all()

    def get_serializer_class(self):
        return TagSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class TagRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for managing detailed tags.

    Provides GET, PUT, PATCH, DELETE methods for Tag instances.
    PUT, PATCH, DELETE methods available for users with administrator permissions.
    """
    def get_queryset(self):
        return Tag.objects.all()

    def get_serializer_class(self):
        return TagSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class PostListCreateAPIView(ListCreateAPIView):
    """
    API endpoint for managing posts.

    Provides GET, POST methods for Post instances.
    """
    pagination_class = PostPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='The status of the posts. '
                            'Available for users with administrator permissions.'
                            'Status values: all, draft, published',
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return a queryset of Post instances based on user permissions and status filter.

        Admins or owners can access all posts or drafts if 'status' is specified.
        Non-owners see only published posts.
        Optimizes queries with select_related and prefetch_related.
        """
        status = self.request.query_params.get('status', None)
        is_access = is_owner_or_superuser(self.request, self)

        if status is not None and is_access:
            if status == 'all':
                return Post.objects.prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')
            elif status == 'draft':
                return Post.draft.prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')
        return Post.published.prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostListSerializer
        elif self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return NotFound('Method Not allowed')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class PostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for managing detailed posts.

    Provides GET, PUT, PATCH, DELETE methods for Post instances.
    """
    def get_queryset(self):
        """
        Return a queryset of Post instances based on user permissions and status filter.

        Admins or owners can access all posts or drafts if 'status' is specified.
        Non-owners see only published posts.
        Optimizes queries with select_related and prefetch_related.
        """
        status = self.request.query_params.get('status', None)
        is_access = is_owner_or_superuser(self.request, self)

        if status is not None and is_access:
            if status == 'all':
                return Post.objects.prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')
            elif status == 'draft':
                return Post.draft.prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')
        return Post.published.prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostRetrieveSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return NotFound('Method Not allowed')

    def get_permissions(self):
        return [IsOwnerOrReadOnlyOrSuperuser()]


class CommentListCreateAPIView(ListCreateAPIView):
    """
    API endpoint for managing comments.

    Provides GET, POST methods for Comment instances.
    """
    pagination_class = CommentPagination


    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='The status of the comments. '
                            'Available for users with administrator permissions.'
                            'Status values: all, disabled, active',
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


    def get_queryset(self):
        """
        Return a queryset of Comment instances based on user permissions and status filter.

        Admins can access all comments if 'status' is specified.
        Non-admins see only active comments.
        Optimizes queries with select_related.
        """
        status = self.request.query_params.get('status', None)
        is_access = is_owner_or_superuser(self.request, self)

        if status is not None and is_access:
            if status == 'all':
                return Comment.objects.all()
            elif status == 'disabled':
                return Comment.objects.filter(active=False)
        return Comment.objects.filter(active=True)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentReadSerializer
        return CommentCreateSerializer

    def get_permissions(self):
        return [IsAuthenticatedOrReadOnly()]


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint for managing detailed comments.

    Provides GET, PUT, PATCH, DELETE methods for Comment instances.
    """
    def get_queryset(self):
        """
        Return a queryset of Comment instances based on user permissions and status filter.

        Admins can access all comments if 'status' is specified.
        Non-admins see only active comments.
        Optimizes queries with select_related.
        """
        is_access = is_owner_or_superuser(self.request, self)
        if is_access:
            return Comment.objects.select_related('user', 'post')
        return Comment.objects.filter(
            active=True).select_related('user', 'post')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentReadSerializer
        return CommentUpdateSerializer


    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticatedOrReadOnly()]
        return [IsSuperuser()]


class SearchAPIView(APIView):
    """
    API endpoint for searching posts.
    """
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='query',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query',
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search status. '
                            'Available for users with administrator permissions.'
                            'Status values: all, draft, published.',
            )
        ]
    )
    def get(self, request):
        status = request.query_params.get('status', None)
        query = self.request.query_params.get('query', None)
        search_rating = 0.1
        is_access = is_owner_or_superuser(self.request, self)

        if query is not None:
            if status == 'all' and is_access:
                posts = Post.objects.annotate(
                    similarity=TrigramSimilarity('title', query)
                ).filter(similarity__gte=search_rating
                         ).order_by('-similarity').prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')
            elif status == 'draft' and is_access:
                posts = Post.draft.annotate(
                    similarity=TrigramSimilarity('title', query)
                ).filter(similarity__gte=search_rating
                         ).order_by('-similarity').prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')
            else:
                posts = Post.published.annotate(
                    similarity=TrigramSimilarity('title', query)
                ).filter(similarity__gte=search_rating
                         ).order_by('-similarity').prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')

            paginator = PostPagination()
            page = paginator.paginate_queryset(posts, request)

            serializer = PostListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response()

    def get_queryset(self):
        return Post.published.all()


class LikeAPIView(GenericAPIView):
    """
    API endpoint for liking posts.
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        post_id = serializer.data['post']
        post = Post.objects.get(pk=post_id)

        if post.users_liked.filter(id=user.id).exists():
            post.users_liked.remove(user)
            return Response(
                {'detail': f'User {user.username} unliked post {post}'}
            )

        if post.users_disliked.filter(id=user.id).exists():
            post.users_disliked.remove(user)
        post.users_liked.add(user)

        return Response(
            {'detail': f'User {user.username} liked post {post}'}
        )


class DislikeAPIView(GenericAPIView):
    """
    API endpoint for disliking posts.
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        post_id = serializer.data['post']
        post = Post.objects.get(pk=post_id)

        if post.users_disliked.filter(id=user.id).exists():
            post.users_disliked.remove(user)
            return Response(
                {'detail': f'User {user.username} undisliked post {post}'}
            )

        if post.users_liked.filter(id=user.id).exists():
            post.users_liked.remove(user)
        post.users_disliked.add(user)

        return Response(
            {'detail': f'User {user.username} disliked post {post}'}
        )


class PopularPostListAPIView(ListAPIView):
    """
    API endpoint for representing popular posts.
    """
    def get_queryset(self):
        redis_client = StrictRedis.from_url(settings.REDIS_URL)
        posts_ids = redis_client.zrevrange('popular_posts', 0, 9)
        return Post.published.filter(id__in=posts_ids).prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author').order_by('-likes')

    def get_serializer_class(self):
        return PostListSerializer
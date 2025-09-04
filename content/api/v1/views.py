from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import permissions
from content.models import Post, Comment
from taggit.models import Tag
from .serializers import (PostReadSerializer,
                          PostCreateUpdateSerializer,
                          TagSerializer,
                          CommentReadSerializer,
                          CommentCreateUpdateSerializer,
                          LikeSerializer)
from content.api.permissions import (IsSuperuser,
                                     IsOwnerOrReadOnlyOrSuperuser,
                                     is_owner_or_superuser)


class PaginationMixin:
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
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class PostPagination(PaginationMixin, PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20


class CommentPagination(PaginationMixin, PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class TagViewSet(ModelViewSet):
    pagination_class = TagPagination
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Tag.objects.all()

    def get_serializer_class(self):
        return TagSerializer


class PostViewSet(ModelViewSet):
    pagination_class = PostPagination
    
    def get_queryset(self):
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

        if self.action != 'list' and is_access:
            return Post.objects.prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')

        return Post.published.prefetch_related(
                    'tags', 'users_liked', 'users_disliked'
                ).select_related('author')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PostReadSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return NotFound("Method not allowed")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [IsOwnerOrReadOnlyOrSuperuser()]


class SearchAPIView(APIView):
    def get(self, request):
        context = {'action': 'search'}
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

            serializer = PostReadSerializer(page, many=True, context=context)
            return paginator.get_paginated_response(serializer.data)
        return Response()

    def get_queryset(self):
        return Post.published.all()


class CommentViewSet(ModelViewSet):
    pagination_class = CommentPagination

    def get_queryset(self):
        status = self.request.query_params.get('status', None)
        is_access = is_owner_or_superuser(self.request, self)

        if self.action != 'list' and is_access:
            return Comment.objects.all().select_related('user', 'post')

        if status is not None and is_access:
            if status == 'all':
                return Comment.objects.all().select_related('user', 'post')
            elif status == 'disabled':
                return Comment.objects.filter(
                    active=False).select_related('user', 'post')
        return Comment.objects.filter(
            active=True).select_related('user', 'post')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CommentReadSerializer
        return CommentCreateUpdateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.IsAuthenticatedOrReadOnly()]
        return [IsSuperuser()]


class LikeAPIView(GenericAPIView):
    serializer_class = LikeSerializer

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
    serializer_class = LikeSerializer

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
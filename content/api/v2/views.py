from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from content.models import Post, Comment
from taggit.models import Tag
from .serializers import (PostReadSerializer,
                          PostCreateUpdateSerializer,
                          TagSerializer,
                          CommentReadSerializer,
                          CommentCreateUpdateSerializer)
from content.api.permissions import (IsSuperuser,
                                     IsOwnerOrSuperuser,
                                     IsOwnerOrReadOnlyOrSuperuser)


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


class TagCreateListAPIView(ListCreateAPIView):
    pagination_class = TagPagination

    def get_queryset(self):
        return Tag.objects.all()

    def get_serializer_class(self):
        return TagSerializer


class TagRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Tag.objects.all()

    def get_serializer_class(self):
        return TagSerializer


class PostListCreateAPIView(ListCreateAPIView):
    pagination_class = PostPagination

    def get_queryset(self):
        status = self.request.query_params.get('status', None)

        permission = IsOwnerOrSuperuser()
        is_access = permission.has_object_permission(self.request, self)

        if status is not None and is_access:
            if status == 'all':
                return Post.objects.all()
            elif status == 'draft':
                return Post.draft.all()
        return Post.published.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostReadSerializer
        elif self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return NotFound('Method Not allowed')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == 'GET':
            context['action'] = 'list'
        elif self.request.method == 'POST':
            context['action'] = 'create'
        return context

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class PostRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        status = self.request.query_params.get('status', None)

        permission = IsOwnerOrSuperuser()
        is_access = permission.has_object_permission(self.request, self)

        if status is not None and is_access:
            if status == 'all':
                return Post.objects.all()
            elif status == 'draft':
                return Post.draft.all()
        return Post.published.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostReadSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return NotFound('Method Not allowed')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == 'GET':
            context['action'] = 'retrieve'
        elif self.request.method == 'POST':
            context['action'] = 'update'
        elif self.request.method == 'PATCH':
            context['action'] = 'partial_update'
        return context

    def get_permissions(self):
        return [IsOwnerOrReadOnlyOrSuperuser()]


class SearchAPIView(APIView):
    def get(self, request):
        context = {'action': 'search'}
        status = request.query_params.get('status', None)
        query = self.request.query_params.get('query', None)
        search_rating = 0.1

        permission = IsSuperuser()
        is_access = permission.has_permission(self.request, self)

        if query is not None:
            if status == 'all' and is_access:
                posts = Post.objects.annotate(
                    similarity=TrigramSimilarity('title', query)
                ).filter(similarity__gte=search_rating).order_by('-similarity')
            elif status == 'draft' and is_access:
                posts = Post.draft.annotate(
                    similarity=TrigramSimilarity('title', query)
                ).filter(similarity__gte=search_rating).order_by('-similarity')
            else:
                posts = Post.published.annotate(
                    similarity=TrigramSimilarity('title', query)
                ).filter(similarity__gte=search_rating).order_by('-similarity')

            paginator = PostPagination()
            page = paginator.paginate_queryset(posts, request)

            serializer = PostReadSerializer(page, many=True, context=context)
            return paginator.get_paginated_response(serializer.data)
        return Response()

    def get_queryset(self):
        return Post.published.all()


class CommentListCreateAPIView(ListCreateAPIView):
    pagination_class = CommentPagination

    def get_queryset(self):
        status = self.request.query_params.get('status', None)

        permission = IsSuperuser()
        is_access = permission.has_permission(self.request, self)

        if status is not None and is_access:
            if status == 'all':
                return Comment.objects.all()
            elif status == 'disabled':
                return Comment.objects.filter(active=False)
        return Comment.objects.filter(active=True)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentReadSerializer
        return CommentCreateUpdateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == 'GET':
            context['action'] = 'list'
        elif self.request.method == 'POST':
            context['action'] = 'create'
        return context

    def get_permissions(self):
        return [IsAuthenticatedOrReadOnly()]


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Comment.objects.filter(active=True)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentReadSerializer
        return CommentCreateUpdateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == 'GET':
            context['action'] = 'retrieve'
        elif self.request.method == 'POST':
            context['action'] = 'update'
        elif self.request.method == 'PATCH':
            context['action'] = 'partial_update'
        return context

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticatedOrReadOnly()]
        return [IsSuperuser()]
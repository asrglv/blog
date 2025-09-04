from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (PostViewSet,
                    TagViewSet,
                    SearchAPIView,
                    CommentViewSet,
                    LikeAPIView,
                    DislikeAPIView)


router = SimpleRouter()
router.register(r'posts', PostViewSet, basename='posts')
router.register('tags', TagViewSet, basename='tags')
router.register(r'comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('like/', LikeAPIView.as_view(), name='like'),
    path('dislike/', DislikeAPIView.as_view(), name='dislike'),
    path('search/', SearchAPIView.as_view(), name='search'),
    path('', include(router.urls)),
]
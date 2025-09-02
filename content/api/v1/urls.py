from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import PostViewSet, TagViewSet, SearchAPIView


router = SimpleRouter()
router.register(r'posts', PostViewSet, basename='posts')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('posts/search/', SearchAPIView.as_view(), name='search'),
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import PostViewSet, TagViewSet


router = SimpleRouter()
router.register(r'posts', PostViewSet, basename='posts')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]
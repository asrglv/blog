from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserModelViewSet


router = SimpleRouter()
router.register(r'users', UserModelViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
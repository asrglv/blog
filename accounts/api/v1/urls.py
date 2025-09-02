from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserModelViewSet
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenBlacklistView)


router = SimpleRouter()
router.register(r'users', UserModelViewSet, basename='users')

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('auth/token/blacklist/', TokenBlacklistView.as_view(),
         name='token_blacklist'),
    path('', include(router.urls)),
]
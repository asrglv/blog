from django.urls import path
from .views import (UserListCreateAPIView,
                    UserRetrieveUpdateDestroyAPIView,
                    ChangePasswordAPIView)
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenBlacklistView)


urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('auth/token/blacklist/', TokenBlacklistView.as_view(),
         name='token_blacklist'),
    path('users/', UserListCreateAPIView.as_view(),
         name='user-list'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyAPIView.as_view(),
         name='user-detail'),
    path('change-password/', ChangePasswordAPIView.as_view(),
         name='change-password'),
]
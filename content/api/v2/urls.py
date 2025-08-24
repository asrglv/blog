from django.urls import path
from .views import (PostListCreateAPIView,
                    PostRetrieveUpdateDestroyAPIView,
                    TagCreateListAPIView,
                    TagRetrieveUpdateDestroyAPIView)


urlpatterns = [
    path('posts/', PostListCreateAPIView.as_view(),
         name='post-list'),
    path('posts/<int:pk>/', PostRetrieveUpdateDestroyAPIView.as_view(),
         name='post-detail'),
    path('tags/', TagCreateListAPIView.as_view(),
         name='tag-list'),
    path('tags/<int:pk>/', TagRetrieveUpdateDestroyAPIView.as_view(),
         name='tag-detail'),
]
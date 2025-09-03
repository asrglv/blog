from django.urls import path
from .views import (PostListCreateAPIView,
                    PostRetrieveUpdateDestroyAPIView,
                    TagCreateListAPIView,
                    TagRetrieveUpdateDestroyAPIView,
                    SearchAPIView,
                    CommentListCreateAPIView,
                    CommentRetrieveUpdateDestroyAPIView)


urlpatterns = [
    path('search/', SearchAPIView.as_view(),
         name='search'),
    path('comments/', CommentListCreateAPIView.as_view(),
         name='comments'),
    path('comments/<int:pk>/',
         CommentRetrieveUpdateDestroyAPIView.as_view(),
         name='comment-detail'),
    path('posts/', PostListCreateAPIView.as_view(),
         name='post-list'),
    path('posts/<int:pk>/', PostRetrieveUpdateDestroyAPIView.as_view(),
         name='post-detail'),
    path('tags/', TagCreateListAPIView.as_view(),
         name='tag-list'),
    path('tags/<int:pk>/', TagRetrieveUpdateDestroyAPIView.as_view(),
         name='tag-detail'),
]
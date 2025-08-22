from rest_framework import serializers
from content.models import Post


class PostReadSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()
    author_email = serializers.StringRelatedField(
        read_only=True,
        source='author'
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author_id', 'author_username',
                  'author_email', 'body', 'publish', 'created_at',
                  'updated_at', 'users_liked', 'users_disliked', 'status']

    def get_author_username(self, obj):
        return obj.author.username


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'author', 'body', 'status']

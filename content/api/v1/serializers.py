from rest_framework import serializers
from content.models import Post, Comment
from taggit.models import Tag
from taggit.serializers import TagListSerializerField


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tag model.

    Used for representing, creating and updating tags.
    """
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'


class SimilarPostsSerializer(serializers.ModelSerializer):
    """
    Serializer for similar posts.

    Used for representing similar posts.
    """
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'tags']


class PostReadSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.

    Used for representing posts.
    """
    tags = TagSerializer(many=True, read_only=True)
    author_username = serializers.SerializerMethodField()
    author_email = serializers.StringRelatedField(
        read_only=True,
        source='author'
    )
    users_liked = serializers.StringRelatedField(many=True, read_only=True)
    users_disliked = serializers.StringRelatedField(many=True, read_only=True)
    similar_posts = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author_id',
                  'author_username', 'author_email', 'body',
                  'publish', 'created_at', 'updated_at',
                  'likes', 'users_liked', 'dislikes', 'users_disliked',
                  'comments_count', 'comments', 'tags', 'similar_posts',
                  'status']

    def get_author_username(self, obj):
        return obj.author.username

    def get_similar_posts(self, obj):
        tags_ids = obj.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(
            tags__in=tags_ids).exclude(id=obj.id).distinct()
        return SimilarPostsSerializer(similar_posts, many=True).data

    def get_comments(self, obj):
        comments = obj.comments.select_related('user').filter(active=True)[:5]
        return CommentReadSerializer(comments, many=True).data

    def get_fields(self):
        fields = super().get_fields()
        if self.context['action'] in ['list', 'search']:
            fields.pop('similar_posts')
            fields.pop('users_liked')
            fields.pop('users_disliked')
            fields.pop('comments')
        return fields


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.

    Used for creating and updating posts.
    """
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'tags', 'status']

    def create(self, validated_data):
        """
        Sets the authenticated user as the author and assigns tags

        after the post is created.
        """
        tags = validated_data.pop('tags')
        user = self.context['request'].user
        validated_data['author'] = user
        post = super().create(validated_data)
        if tags is not None:
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        """
        Assigns tags if provided in validated_data and updates other fields.
        """
        tags = validated_data.pop('tags')
        if tags is not None:
            instance.tags.set(tags)
        return super().update(instance, validated_data)


class CommentReadSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.

    Used for representing comments.
    """
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.

    Used for creating and updating comments.
    """
    class Meta:
        model = Comment
        fields = ['id', 'post', 'body', 'active']

    def create(self, validated_data):
        """
        Sets the authenticated user as the comment's user.
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def get_fields(self):
        """
        Removes the 'active' field for non-superusers.
        """
        fields = super().get_fields()
        user = self.context['request'].user
        if not user.is_superuser:
            fields.pop('active')
        return fields


class LikeSerializer(serializers.Serializer):
    """
    Serializer for like and dislike functions.

    Used for validating post.
    """
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.published.all(),
    )

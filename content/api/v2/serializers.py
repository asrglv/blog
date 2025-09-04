from rest_framework import serializers
from content.models import Post, Comment
from taggit.models import Tag
from taggit.serializers import TagListSerializerField


class TagSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'


class SimilarPostsSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'tags']


class PostReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author_username = serializers.SerializerMethodField()
    author_email = serializers.StringRelatedField(
        read_only=True,
        source='author'
    )
    similar_posts = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author_id',
                  'author_username', 'author_email', 'body',
                  'publish', 'created_at', 'updated_at',
                  'users_liked', 'users_disliked',
                  'similar_posts', 'tags', 'status']

    def get_author_username(self, obj):
        return obj.author.username

    def get_similar_posts(self, obj):
        tags_ids = obj.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(
            tags__in=tags_ids).exclude(id=obj.id).distinct()
        return SimilarPostsSerializer(similar_posts, many=True).data

    def get_fields(self):
        fields = super().get_fields()
        if self.context['action'] in ['list', 'search']:
            fields.pop('similar_posts')
        return fields


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Post
        fields = ['title', 'body', 'tags', 'status']

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        user = self.context['request'].user
        validated_data['author'] = user
        post = super().create(validated_data)
        if tags is not None:
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        if tags is not None:
            instance.tags.set(tags)
        return super().update(instance, validated_data)


class CommentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['post', 'body', 'active']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user
        if not user.is_superuser:
            fields.pop('active')
        return fields
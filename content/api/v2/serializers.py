from rest_framework import serializers
from content.models import Post
from taggit.models import Tag


class TagSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'


class PostReadSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()
    author_email = serializers.StringRelatedField(
        read_only=True,
        source='author'
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author_id',
                  'author_username', 'author_email', 'body',
                  'publish', 'created_at', 'updated_at',
                  'users_liked', 'users_disliked', 'tags', 'status']

    def get_author_username(self, obj):
        return obj.author.username

    def get_tags(self, obj):
        return TagSerializer(obj.tags.all(), many=True).data


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Post
        fields = ['title', 'author', 'body', 'tags', 'status']

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        post = super().create(validated_data)
        if tags is not None:
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        if tags is not None:
            instance.tags.set(tags)
        return super().update(instance, validated_data)

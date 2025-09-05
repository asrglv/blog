from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from taggit.managers import TaggableManager


USER = settings.AUTH_USER_MODEL


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class DraftManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='draft')


class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    author = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users_liked = models.ManyToManyField(USER, related_name='liked_posts',
                                         blank=True)
    likes = models.PositiveIntegerField(default=0)
    users_disliked = models.ManyToManyField(USER, related_name='disliked_posts',
                                            blank=True)
    dislikes = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10,
                              choices=Status.choices,
                              default=Status.DRAFT)
    tags = TaggableManager()
    objects = models.Manager()
    published = PublishedManager()
    draft = DraftManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.title):
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE,
                             related_name='commented_on')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"

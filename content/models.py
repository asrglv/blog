from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from taggit.managers import TaggableManager


USER = settings.AUTH_USER_MODEL


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    author = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users_liked = models.ManyToManyField(USER, related_name='liked_posts')
    users_disliked = models.ManyToManyField(USER, related_name='disliked_posts')
    status = models.CharField(max_length=10,
                              choices=Status.choices,
                              default=Status.DRAFT)
    tags = TaggableManager()
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.title):
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

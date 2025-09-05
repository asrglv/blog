from django.db import models
from django.db.models.signals import (m2m_changed,
                                      post_save,
                                      pre_save,
                                      post_delete)
from django.dispatch import receiver
from content.models import Post, Comment
from redis import StrictRedis
from django.conf import settings


@receiver(m2m_changed, sender=Post.users_liked.through)
def users_liked_change(sender, instance, **kwargs):
    """
    Signal handler to update the number of likes on a post
    when the many-to-many relation 'users_liked' changes.
    """
    instance.likes = instance.users_liked.count()
    instance.save(update_fields=['likes'])

    # Connect to Redis and update the ZSET storing popular posts:
    redis_client = StrictRedis.from_url(settings.REDIS_URL)
    redis_client.zadd('popular_posts',
                      {instance.pk: instance.likes})

    redis_client.zremrangebyrank('popular_posts', 0, -11)


@receiver(m2m_changed, sender=Post.users_disliked.through)
def users_disliked_change(sender, instance, **kwargs):
    """
    Signal handler to update the number of likes on a post
    when the many-to-many relation 'users_disliked' changes.
    """
    instance.dislikes = instance.users_disliked.count()
    instance.save()

    # Connect to Redis and update the ZSET storing popular posts:
    redis_client = StrictRedis.from_url(settings.REDIS_URL)
    redis_client.zadd('popular_posts',
                      {instance.pk: instance.likes})

    redis_client.zremrangebyrank('popular_posts', 0, -11)


@receiver(post_save, sender=Comment)
def increment_post_comments_count(sender, instance, created, raw, **kwargs):
    """
    Signal handler to increment the comments_count field
    when a new comment is created for a post.
    """
    if raw:
        return
    if created:
        Post.objects.filter(pk=instance.post.pk).update(
            comments_count=models.F('comments_count') + 1
        )


@receiver(post_delete, sender=Comment)
def decrement_post_comments_count(sender, instance, raw, **kwargs):
    """
    Signal handler to decrement the comments_count field
    when a comment is deleted from a post.
    """
    if raw:
        return
    Post.objects.filter(pk=instance.post.pk).update(
        comments_count=models.F('comments_count') - 1
    )




@receiver(pre_save, sender=Comment)
def increment_or_decrement_post_comments_count(sender, instance, raw, **kwargs):
    """
    Signal handler to adjust the comments_count field
    when the 'active' status of a comment changes.
    """
    if raw:
        return
    if not instance.pk:
        return

    comment = Comment.objects.get(pk=instance.pk)
    if comment.active != instance.active:
        if instance.active:
            Post.objects.filter(pk=instance.post.pk).update(
                comments_count=models.F('comments_count') + 1
            )
        else:
            Post.objects.filter(pk=instance.post.pk).update(
                comments_count=models.F('comments_count') - 1
            )
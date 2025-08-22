from django.contrib import admin
from content.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'author', 'publish',
                    'created_at', 'updated_at', 'status']
    list_display_links = ['id', 'title', 'slug']
    list_filter = ['status', 'publish', 'created_at', 'updated_at']
    search_fields = ['id', 'title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
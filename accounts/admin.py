from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'surname', 'email', 'created_at',
                    'updated_at', 'is_superuser']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['username', 'name', 'surname', 'email']
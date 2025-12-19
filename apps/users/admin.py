from django.contrib import admin

from apps.users import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'role', 'is_admin', 'email_verified', 'created_at']
    list_filter = ['role', 'is_admin', 'email_verified', 'created_at']
    search_fields = ['username', 'email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('email',)
        }),
        ('Permissions', {
            'fields': ('role', 'is_admin', 'email_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

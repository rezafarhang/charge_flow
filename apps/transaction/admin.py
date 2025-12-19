from django.contrib import admin
from apps.transaction import models


@admin.register(models.Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'balance']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['balance']
    raw_id_fields = ['user']


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'status', 'from_type', 'to_type', 'created_at', 'updated_at']
    list_filter = ['status', 'from_type', 'to_type', 'created_at']
    search_fields = ['from_user__username', 'to_phone__phone_number']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['from_wallet', 'from_user', 'to_wallet', 'to_phone', 'updated_by']
    ordering = ['-created_at']

    fieldsets = (
        ('Transaction Details', {
            'fields': ('amount', 'status')
        }),
        ('Source', {
            'fields': ('from_type', 'from_wallet', 'from_user')
        }),
        ('Destination', {
            'fields': ('to_type', 'to_wallet', 'to_phone')
        }),
        ('Timestamps & Updates', {
            'fields': ('created_at', 'updated_at', 'updated_by')
        }),
    )

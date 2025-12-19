from rest_framework import serializers

from apps.transaction import models


class WalletSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = models.Wallet
        fields = ['user_email', 'balance']
        read_only_fields = fields


class CreateCreditRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
    )


class TransactionSerializer(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField(
        source='from_user.id',
        read_only=True,
        allow_null=True
    )
    from_wallet_id = serializers.IntegerField(
        source='from_wallet.id',
        read_only=True,
        allow_null=True
    )
    to_wallet_id = serializers.IntegerField(
        source='to_wallet.id',
        read_only=True,
        allow_null=True
    )
    to_phone_number = serializers.CharField(
        source='to_phone.phone_number',
        read_only=True,
        allow_null=True
    )
    updated_by_id = serializers.IntegerField(
        source='updated_by.id',
        read_only=True,
        allow_null=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = models.Transaction
        fields = [
            'id',
            'amount',
            'status',
            'status_display',
            'created_at',
            'updated_at',
            'updated_by_id',
            'from_type',
            'from_user_id',
            'from_wallet_id',
            'to_type',
            'to_wallet_id',
            'to_phone_number',
        ]
        read_only_fields = fields


class ProcessTransactionSerializer(serializers.Serializer):
    transaction_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=[models.TransactionStatus.APPROVED, models.TransactionStatus.REJECTED,]
    )

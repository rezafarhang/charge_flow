from django.db import models

from apps.users import models as users_models


class Wallet(models.Model):
    user = models.OneToOneField(
        to=users_models.User,
        on_delete=models.CASCADE
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name='wallet_balance_non_negative'
            ),
        ]


class SourceType(models.IntegerChoices):
    WALLET = 1
    USER = 2


class DestType(models.IntegerChoices):
    WALLET = 1
    PHONE = 2


class TransactionStatus(models.IntegerChoices):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3


class Transaction(models.Model):
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    status = models.SmallIntegerField(
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING.value,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        users_models.User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='updated_transactions'
    )

    from_type = models.SmallIntegerField(
        choices=SourceType.choices,
    )
    from_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name='sent_transactions',
    )
    from_user = models.ForeignKey(
        users_models.User,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name='sent_transactions',
    )

    to_type = models.SmallIntegerField(
        choices=DestType.choices
    )
    to_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name='received_transactions',
    )
    to_phone = models.ForeignKey(
        users_models.PhoneNumber,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name='received_transactions',
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                        models.Q(
                            from_type=SourceType.WALLET,
                            from_wallet__isnull=False,
                            from_user__isnull=True
                        ) |
                        models.Q(
                            from_type=SourceType.USER,
                            from_wallet__isnull=True,
                            from_user__isnull=False
                        )
                ),
                name='valid_source'
            ),
            models.CheckConstraint(
                check=(
                        models.Q(
                            to_type=DestType.WALLET,
                            to_wallet__isnull=False,
                            to_phone__isnull=True
                        ) |
                        models.Q(
                            to_type=DestType.PHONE,
                            to_wallet__isnull=True,
                            to_phone__isnull=False
                        )
                ),
                name='valid_destination'
            ),
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name='transaction_amount_positive'
            ),
        ]
        indexes = [
            models.Index(fields=['status', 'created_at'], name='tx_status_created_idx'),
            models.Index(fields=['from_wallet', 'status'], name='tx_from_wallet_status_idx'),
            models.Index(fields=['to_wallet', 'status'], name='tx_to_wallet_status_idx'),
            models.Index(fields=['to_phone', 'status'], name='tx_to_phone_status_idx'),
            models.Index(fields=['status', 'updated_at'], name='tx_status_updated_idx'),
        ]

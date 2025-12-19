from django.db import transaction
from django.db.models import F
from django.utils import timezone

from rest_framework import exceptions

from apps.transaction import models, consts
from apps.users import consts as user_consts


class CreditRequestService:
    @staticmethod
    def create_credit_request(user, amount):
        if amount <= 0:
            raise exceptions.ValidationError(
                consts.TransactionErrorConsts.InvalidAmount().get_status()
            )

        # Get or create wallet for user
        try:
            wallet = models.Wallet.objects.get(user=user)
        except models.Wallet.DoesNotExist:
            raise exceptions.NotFound(
                consts.TransactionErrorConsts.WalletNotFound().get_status()
            )

        # Create pending transaction (USER -> WALLET)
        trc = models.Transaction.objects.create(
            amount=amount,
            status=models.TransactionStatus.PENDING,
            from_type=models.SourceType.USER,
            from_user=user,
            to_type=models.DestType.WALLET,
            to_wallet=wallet
        )

        return trc

    @staticmethod
    def approve_credit_request(transaction_id, admin_user):
        if not admin_user.is_admin and admin_user.role != user_consts.UserRole.ADMIN:
            raise exceptions.PermissionDenied(
                consts.TransactionErrorConsts.PermissionDenied().get_status()
            )

        with transaction.atomic():
            # Try to update transaction status from PENDING to APPROVED atomically
            # This ensures only one admin can approve this transaction
            affected = models.Transaction.objects.filter(
                id=transaction_id,
                status=models.TransactionStatus.PENDING
            ).update(
                status=models.TransactionStatus.APPROVED,
                updated_at=timezone.now(),
                updated_by=admin_user
            )

            if affected == 0:
                # Transaction either doesn't exist or is already processed
                try:
                    trc = models.Transaction.objects.get(id=transaction_id)
                    # Transaction exists but not pending
                    raise exceptions.ValidationError(
                        consts.TransactionErrorConsts.AlreadyProcessed().get_status()
                    )
                except models.Transaction.DoesNotExist:
                    raise exceptions.NotFound(
                        consts.TransactionErrorConsts.TransactionNotFound().get_status()
                    )

            # Get the updated transaction
            trc = models.Transaction.objects.get(id=transaction_id)

            # Atomic Update
            models.Wallet.objects.filter(
                id=trc.to_wallet_id
            ).update(
                balance=F('balance') + trc.amount
            )

        return trc


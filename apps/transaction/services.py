from django.db import transaction, IntegrityError
from django.db.models import F
from django.utils import timezone

from rest_framework import exceptions

from apps.transaction import models, consts
from apps.users import consts as user_consts, models as users_models


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
    def update_status_credit_request(transaction_id, admin_user, status):
        with transaction.atomic():
            # Try to update transaction status from PENDING to APPROVED atomically
            # This ensures only one admin can approve this transaction
            affected = models.Transaction.objects.filter(
                id=transaction_id,
                status=models.TransactionStatus.PENDING
            ).update(
                status=status,
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

            if status == models.TransactionStatus.APPROVED:
                # Atomic Update
                models.Wallet.objects.filter(
                    id=trc.to_wallet_id
                ).update(
                    balance=F('balance') + trc.amount
                )

        return trc


class ChargeService:
    @staticmethod
    def sell_charge(user, phone_number, amount):
        if amount <= 0:
            raise exceptions.ValidationError(
                consts.TransactionErrorConsts.InvalidAmount
            )

        try:
            wallet = models.Wallet.objects.get(user=user)
        except models.Wallet.DoesNotExist:
            raise exceptions.NotFound(
                consts.TransactionErrorConsts.WalletNotFound().get_status()
            )

        try:
            phone = users_models.PhoneNumber.objects.get(phone_number=phone_number)
        except users_models.PhoneNumber.DoesNotExist:
            raise exceptions.NotFound(
                consts.TransactionErrorConsts.PhoneNumberNotFound().get_status()
            )

        with transaction.atomic():
            try:
                affected = models.Wallet.objects.filter(
                    id=wallet.id
                ).update(
                    balance=F('balance') - amount
                )

                if affected == 0:
                    raise exceptions.NotFound(
                        consts.TransactionErrorConsts.WalletNotFound().get_status()
                    )
            except IntegrityError as e:
                # CHECK constraint violated: balance would be negative
                if 'wallet_balance_non_negative' in str(e):
                    raise exceptions.ValidationError(
                        consts.TransactionErrorConsts.InsufficientBalance().get_status()
                    )
                raise exceptions.ValidationError("Something went wrong!")

            # Atomic Update
            users_models.PhoneNumber.objects.filter(
                id=phone.id
            ).update(
                balance=F('balance') + amount
            )

            # Create transaction log (WALLET -> PHONE)
            trc = models.Transaction.objects.create(
                amount=amount,
                status=models.TransactionStatus.APPROVED,
                from_type=models.SourceType.WALLET,
                from_wallet=wallet,
                to_type=models.DestType.PHONE,
                to_phone=phone,
                updated_at=timezone.now(),
                updated_by=user
            )

        return trc

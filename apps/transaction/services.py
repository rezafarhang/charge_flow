from rest_framework import exceptions

from apps.transaction import models, consts


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

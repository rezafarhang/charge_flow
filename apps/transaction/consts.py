from apps.core.decorators import status_decorator


class TransactionErrorConsts:
    @status_decorator
    class InsufficientBalance:
        code = 3001
        message = 'Insufficient balance in wallet.'

    @status_decorator
    class WalletNotFound:
        code = 3002
        message = 'Wallet not found.'

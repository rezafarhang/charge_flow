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

    @status_decorator
    class TransactionNotFound:
        code = 3004
        message = 'Transaction not found.'

    @status_decorator
    class AlreadyProcessed:
        code = 3005
        message = 'Transaction has already been processed.'

    @status_decorator
    class InvalidAmount:
        code = 3006
        message = 'Amount must be greater than zero.'

    @status_decorator
    class PermissionDenied:
        code = 3007
        message = 'You do not have permission to perform this action.'

    @status_decorator
    class InvalidTransactionStatus:
        code = 3008
        message = 'Invalid transaction status for this operation.'

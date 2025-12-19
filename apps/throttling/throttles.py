from rest_framework import throttling


class LoginRateThrottle(throttling.AnonRateThrottle):
    scope = 'login'


class RegistrationRateThrottle(throttling.AnonRateThrottle):
    scope = 'registration'


class UserProfileThrottle(throttling.UserRateThrottle):
    scope = 'user_profile'


class TransactionCreateThrottle(throttling.UserRateThrottle):
    scope = 'transaction_create'


class TransactionListThrottle(throttling.UserRateThrottle):
    scope = 'transaction_list'

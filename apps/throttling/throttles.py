from rest_framework import throttling


class OTPVerificationRateThrottleDay(throttling.UserRateThrottle):
    scope = 'otp_verification_day'


class OTPVerificationRateThrottleHour(throttling.UserRateThrottle):
    scope = 'otp_verification_hour'


class OTPSendRateThrottleDay(throttling.UserRateThrottle):
    scope = 'otp_send_day'


class OTPSendRateThrottleHour(throttling.UserRateThrottle):
    scope = 'otp_send_hour'


class LoginRateThrottle(throttling.AnonRateThrottle):
    scope = 'login'


class RegistrationRateThrottle(throttling.AnonRateThrottle):
    scope = 'registration'

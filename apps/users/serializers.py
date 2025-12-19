from django.contrib.auth.hashers import make_password, check_password

from rest_framework import serializers, exceptions
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users import models, consts
from apps.transaction import models as transaction_models


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=255,
        required=True
    )
    password = serializers.CharField(
        max_length=255,
        required=True,
        write_only=True
    )

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError(
                consts.AuthErrorConsts.EmailRequired().get_status()
            )

        # Check if email already exists
        if models.User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                consts.AuthErrorConsts.EmailAlreadyExists().get_status()
            )

        return value.lower()

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError(
                consts.AuthErrorConsts.PasswordRequired().get_status()
            )

        if len(value) < consts.AuthenticationConsts.MINIMUM_PASSWORD_LENGTH:
            raise serializers.ValidationError(
                consts.AuthErrorConsts.PasswordTooShort().get_status()
            )

        return value

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')

        user = models.User.objects.create(
            email=email,
            username=email,
            password=make_password(password),
            email_verified=True  # TODO: Add Verify Email Endpoint later
        )

        transaction_models.Wallet.objects.create(user=user)
        refresh = RefreshToken.for_user(user)

        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=255,
        required=True
    )
    password = serializers.CharField(
        max_length=255,
        required=True,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = models.User.objects.get(email=email)
        except models.User.DoesNotExist:
            raise serializers.ValidationError(
                consts.AuthErrorConsts.AccountNotFound().get_status()
            )

        if not user.password or not check_password(password, user.password):
            raise serializers.ValidationError(
                consts.AuthErrorConsts.InvalidCredentials().get_status()
            )
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)

        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        max_length=500,
        required=True
    )

    def validate_refresh_token(self, value):
        if not value:
            raise serializers.ValidationError(
                consts.LogoutErrorConsts.RefreshTokenRequired().get_status()
            )
        return value

    def create(self, validated_data):
        refresh_token = validated_data['refresh_token']

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            raise exceptions.ValidationError(
                consts.LogoutErrorConsts.InvalidToken().get_status()
            )

        return {}


class PhoneNumberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = models.PhoneNumber
        fields = ['id', 'phone_number', 'user_email', 'balance']
        read_only_fields = ['id', 'user_email', 'balance']

    def validate(self, attrs):
        user_email = attrs.get('user.email')
        if self.context['request'].user.email != user_email:
            raise exceptions.PermissionDenied(
                consts.PhoneNumberErrorConsts.NotAllowed().get_status()
            )
        # TODO: Send OTP For Strictest Validation
        return attrs

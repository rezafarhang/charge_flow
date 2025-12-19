from rest_framework import status, permissions, views, response, generics

from apps.transaction import services, serializers, models
from apps.throttling import throttles


class WalletBalanceView(generics.RetrieveAPIView):
    serializer_class = serializers.WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [throttles.TransactionListThrottle]

    def get_object(self):
        return models.Wallet.objects.get(user=self.request.user)


class CreateCreditRequestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [throttles.TransactionCreateThrottle]

    def post(self, request):
        serializer = serializers.CreateCreditRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trc = services.CreditRequestService.create_credit_request(
            user=request.user,
            amount=serializer.validated_data.get('amount')
        )
        response_serializer = serializers.TransactionSerializer(trc)
        return response.Response(response_serializer.data, status=status.HTTP_201_CREATED)


class UpdateCreditRequestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [throttles.TransactionCreateThrottle]

    def patch(self, request):
        serializer = serializers.ProcessTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trc = services.CreditRequestService.update_status_credit_request(
            transaction_id=serializer.validated_data.get('transaction_id'),
            admin_user=request.user,
            status=serializer.validated_data.get('status'),
        )
        response_serializer = serializers.TransactionSerializer(trc)
        return response.Response(response_serializer.data, status=status.HTTP_200_OK)


class SellChargeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [throttles.TransactionCreateThrottle]

    def post(self, request):
        serializer = serializers.SellChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trc = services.ChargeService.sell_charge(
            user=request.user,
            phone_number=serializer.validated_data['phone_number'],
            amount=serializer.validated_data['amount']
        )
        response_serializer = serializers.TransactionSerializer(trc)
        return response.Response(response_serializer.data, status=status.HTTP_201_CREATED)

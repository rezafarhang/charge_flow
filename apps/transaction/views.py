from rest_framework import status, permissions, views, response

from apps.transaction import services, serializers, consts, models


class CreateCreditRequestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        serializer = serializers.CreateCreditRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        txn = services.CreditRequestService.create_credit_request(
            user=request.user,
            amount=serializer.validated_data.get('amount')
        )
        response_serializer = serializers.TransactionSerializer(txn)
        return response.Response(response_serializer.data, status=status.HTTP_201_CREATED)


class UpdateCreditRequestView(views.APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def patch(self, request):
        serializer = serializers.ProcessTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        txn = services.CreditRequestService.update_status_credit_request(
            transaction_id=serializer.validated_data.get('transaction_id'),
            admin_user=request.user,
            status=serializer.validated_data.get('status'),
        )
        response_serializer = serializers.TransactionSerializer(txn)
        return response.Response(response_serializer.data, status=status.HTTP_200_OK)

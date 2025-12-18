from rest_framework import status, generics, permissions, response

from apps.users import serializers, models


class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer
    permission_classes = [permissions.AllowAny,]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(
            {
                'access_token': result.get('access_token'),
                'refresh_token': result.get('refresh_token'),
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.CreateAPIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = [permissions.AllowAny,]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(
            {
                'access_token': result.get('access_token'),
                'refresh_token': result.get('refresh_token'),
            },
            status=status.HTTP_200_OK
        )


class LogoutView(generics.CreateAPIView):
    serializer_class = serializers.LogoutSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(
            status=status.HTTP_204_NO_CONTENT
        )

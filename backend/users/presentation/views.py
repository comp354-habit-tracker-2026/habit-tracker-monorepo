from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny

from users.serializers import RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.business.services import PasswordResetService
from users.serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = PasswordResetService()
        result = service.request_reset(serializer.validated_data["email"])

        return Response(result, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = PasswordResetService()
        result = service.confirm_reset(
            serializer.validated_data["token"],
            serializer.validated_data["new_password"]
        )

        return Response(result, status=status.HTTP_200_OK)

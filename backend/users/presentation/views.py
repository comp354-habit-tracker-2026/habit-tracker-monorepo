from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from users.business.services import UserDeletionService

from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import (
    RegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    CustomTokenObtainPairSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        service = UserDeletionService()
        service.execute(request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)

class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"message": "If user exists, reset link sent"},
                status=status.HTTP_200_OK,
            )

        token = default_token_generator.make_token(user)

        return Response(
            {
                "message": "Reset token generated",
                "uid": user.pk,
                "token": token,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["password"]

        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response(
                {"error": "Invalid user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK,
        )


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer
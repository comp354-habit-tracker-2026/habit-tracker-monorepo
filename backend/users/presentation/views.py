from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny

from users.serializers import RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer




from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If user exists, reset link sent"}, status=200)

        token = default_token_generator.make_token(user)

        # In real app → send email
        return Response({
            "message": "Reset token generated",
            "uid": user.pk,
            "token": token
        }, status=200)


class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user_id = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("password")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid user"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid token"}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"}, status=200)

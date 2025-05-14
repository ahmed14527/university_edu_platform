from rest_framework import generics, status, response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .models import UserSession
from . import serializers
from django.contrib.auth.hashers import check_password

User = get_user_model()

# ----------------------------
# 🔐 AUTHENTICATION VIEWS
# ----------------------------

class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            UserSession.objects.create(user=user, access_token=access)

            return Response({
                'access': access,
                'refresh': str(refresh),
                'is_doctor': user.is_doctor,
                'username': user.username,
            })

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            UserSession.objects.filter(user=request.user).delete()

            return Response(status=status.HTTP_205_RESET_CONTENT)

        except Exception:
            return Response(
                {"detail": "Invalid token or already blacklisted"},
                status=status.HTTP_400_BAD_REQUEST
            )


# ----------------------------
# 🔄 PASSWORD RESET VIEWS
# ----------------------------

class PasswordReset(generics.GenericAPIView):
    """
    Generate password reset link.
    """
    serializer_class = serializers.EmailSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "User doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        reset_url = reverse("reset-password", kwargs={"encoded_pk": encoded_pk, "token": token})
        reset_link = f"http://localhost:8000{reset_url}"

        return Response(
            {
                "message": "Reset link generated successfully",
                "reset_link": reset_link
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordAPI(generics.GenericAPIView):
    """
    Reset password using token and encoded_pk.
    """
    serializer_class = serializers.ResetPasswordSerializer
    permission_classes = [AllowAny]

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"kwargs": kwargs}
        )
        serializer.is_valid(raise_exception=True)
        return response.Response(
            {"message": "Password reset complete"},
            status=status.HTTP_200_OK,
        )


# ----------------------------
# 🔁 CHANGE PASSWORD (LOGGED-IN)
# ----------------------------

class ChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password changed successfully. Please login again."}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import DeviceToken
from .serializers import DeviceTokenSerializer
from .utils.firebase_notify import send_firebase_notification
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes


class RegisterDeviceToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']

            # Check if token already exists for another user
            existing = DeviceToken.objects.filter(token=token).exclude(user=request.user)
            if existing.exists():
                return Response({"error": "This token is already used by another user."}, status=400)

            # Save or get token for this user
            obj, created = DeviceToken.objects.get_or_create(
                user=request.user,
                token=token
            )

            message = "Token registered successfully." if created else "Token already registered."
            return Response({"message": message})
        return Response(serializer.errors, status=400)


class SendNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get("user_id")
        title = request.data.get("title")
        body = request.data.get("body")

        if not all([user_id, title, body]):
            return Response({"error": "user_id, title, and body are required."}, status=400)

        try:
            user = User.objects.get(id=user_id)
            tokens = DeviceToken.objects.filter(user=user)
            if not tokens.exists():
                return Response({"error": "No device tokens found for this user."}, status=404)

            responses = []
            for token_obj in tokens:
                try:
                    res = send_firebase_notification(token_obj.token, title, body)
                    responses.append({
                        "token": token_obj.token,
                        "status": "success",
                        "response": res
                    })
                except Exception as e:
                    responses.append({
                        "token": token_obj.token,
                        "status": "failed",
                        "error": str(e)
                    })

            return Response({
                "message": "Notification process complete.",
                "results": responses
            })
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def broadcast_notification(request):
    user_ids = request.data.get("user_ids", [])  # List of user IDs or empty for all
    title = request.data.get("title")
    body = request.data.get("body")

    if not title or not body:
        return Response({"error": "Title and body are required."}, status=400)

    if user_ids:
        users = User.objects.filter(id__in=user_ids)
    else:
        users = User.objects.all()

    results = []
    for user in users:
        tokens = DeviceToken.objects.filter(user=user)
        for token in tokens:
            try:
                res = send_firebase_notification(token.token, title, body)
                results.append({
                    "user": user.username,
                    "token": token.token,
                    "status": "sent",
                    "response": res
                })
            except Exception as e:
                results.append({
                    "user": user.username,
                    "token": token.token,
                    "status": "failed",
                    "error": str(e)
                })

    return Response({
        "message": "Broadcast completed.",
        "results": results
    }, status=status.HTTP_200_OK)

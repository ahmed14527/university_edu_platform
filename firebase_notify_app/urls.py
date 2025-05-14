from django.urls import path
from .views import RegisterDeviceToken, SendNotificationView,broadcast_notification

urlpatterns = [
    path('register-token/', RegisterDeviceToken.as_view(), name='register-token'),
    path('send-notification/', SendNotificationView.as_view(), name='send-notification'),
    path('notifications/broadcast/', broadcast_notification, name='broadcast_notification'),

]

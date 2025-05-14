from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordAPI,
)
from . import views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', views.PasswordReset.as_view(), name='password-reset'),
    path('password-reset/<encoded_pk>/<token>/', views.ResetPasswordAPI.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordAPI.as_view(), name='change-password'),

]

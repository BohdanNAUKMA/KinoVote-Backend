"""Маршрути API застосунку core."""

from django.urls import path

from .views import HealthCheckView, RegisterView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('health/', HealthCheckView.as_view(), name='health'),
]

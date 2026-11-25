"""В'юхи API KinoVote."""

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer


class HealthCheckView(APIView):
    """Перевірка доступності сервісу."""

    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response(
            {'status': 'ok', 'service': 'KinoVote API'},
            status=status.HTTP_200_OK,
        )


class RegisterView(generics.CreateAPIView):
    """Реєстрація нового користувача."""

    serializer_class = RegisterSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)

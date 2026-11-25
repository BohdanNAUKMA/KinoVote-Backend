"""Автотести API KinoVote."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

TEST_PASSWORD = 'Str0ng-Passw0rd!'


class HealthCheckTests(APITestCase):
    """Тести ендпоінта /api/health/."""

    def test_health_returns_ok(self):
        response = self.client.get(reverse('health'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {'status': 'ok', 'service': 'KinoVote API'},
        )


class RegisterTests(APITestCase):
    """Тести реєстрації користувача."""

    def setUp(self):
        self.url = reverse('register')

    def get_payload(self, **overrides):
        payload = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': TEST_PASSWORD,
            'password2': TEST_PASSWORD,
        }
        payload.update(overrides)
        return payload

    def test_register_creates_user(self):
        response = self.client.post(self.url, self.get_payload())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'alice')
        self.assertNotIn('password', response.data)
        user = User.objects.get(username='alice')
        self.assertTrue(user.check_password(TEST_PASSWORD))

    def test_register_rejects_mismatched_passwords(self):
        payload = self.get_payload(password2='An0ther-Passw0rd!')

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)
        self.assertFalse(User.objects.filter(username='alice').exists())

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            username='bob',
            email='alice@example.com',
            password=TEST_PASSWORD,
        )

        response = self.client.post(self.url, self.get_payload())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class JWTTokenTests(APITestCase):
    """Тести отримання та оновлення JWT-токенів."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password=TEST_PASSWORD,
        )

    def test_obtain_token_pair(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'alice', 'password': TEST_PASSWORD},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_with_wrong_password(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'alice', 'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        tokens = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'alice', 'password': TEST_PASSWORD},
        ).data

        response = self.client.post(
            reverse('token_refresh'),
            {'refresh': tokens['refresh']},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

import json

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch


class AuthenticationGatewayViewTests(APITestCase):
    def setUp(self) -> None:
        self.register_url = reverse("register-list")
        self.login_url = reverse("login-list")

        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "User",
            "last_name": "Test",
            "password": "testpassword123",
            "password_confirmation": "testpassword123",
            "phone": "123456789",
            "role": "Patient"
        }

        self.invalid_user_data_1 = {
            "username": "testuser",
            "email": "testuser@example.com",
            "first_name": "",
            "last_name": "",
            "password": "testpassword123",
            "password_confirmation": "testpassword123",
            "phone": "123456789",
            "role": "Patient"
        }

        self.invalid_user_data_2 = {
            "username": "testuser",
            "email": "",
            "first_name": "User",
            "last_name": "Test",
            "password": "testpassword123",
            "password_confirmation": "testpassword123",
            "phone": "",
            "role": "Patient"
        }

    @patch("api_accounts.views.forward_request_to_service")
    def test_login_successful(self, mock_forward_request):
        mock_forward_request.return_value.status_code = 200
        mock_forward_request.return_value.json.return_value = {
            "access": "mock_access_token",
            "refresh": "mock_refresh_token"
        }

        login_response = self.client.post(
            self.login_url,
            data=json.dumps({"username": "testuser", "password": "testpassword123"}),
            content_type="application/json"
        )
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.json())
        self.assertIn("refresh", login_response.json())

    def test_login_missing_data(self):
        login_response = self.client.post(
            self.login_url,
            data=json.dumps({"username": "", "password": ""}),
            content_type="application/json"
        )
        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('Missing username or password', login_response.json()["error"])

    @patch("api_accounts.views.forward_request_to_service")
    def test_login_service_error(self, mock_forward_request):
        mock_forward_request.return_value.status_code = 401
        mock_forward_request.return_value.json.return_value = {
            "detail": "Invalid credentials"
        }

        response = self.client.post(
            self.login_url,
            data=json.dumps({"username": "testuser", "password": "testpassword123"}),
            content_type="application/json"
        )
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Invalid credentials")

    @patch("api_accounts.views.forward_request_to_service")
    def test_register_successful(self, mock_forward_request):
        mock_forward_request.return_value.status_code = 201
        mock_forward_request.return_value.json.return_value = {
            'data': self.user_data
        }

        response = self.client.post(
            self.register_url,
            data=json.dumps(self.user_data),
            content_type="application/json"
        )
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_invalid_json(self):
        response = self.client.post(
            self.register_url,
            data=self.user_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('Invalid JSON format', response.json()['error'])

# Nie wywołuje się moc poniważ nie dochodzi do wysłania post.
    def test_register_missing_name_lastname(self):
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.invalid_user_data_1),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('First and last name are required', response.json()['error'])

    def test_register_missing_email_phone(self):
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.invalid_user_data_2),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('email and phone are required', response.json()['error'])

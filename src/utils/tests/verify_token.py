from unittest.mock import patch

import jwt
from rest_framework import status
from django.test import TestCase

from core.settings import TOKEN_URL
from utils.support_functions import verify_token


class VerifyTokenTests(TestCase):
    def create_valid_jwt_token(self):
        payload = {
            "sub": "1234567890",
            "name": "Test User",
            "iat": 1516239022,
            "exp": 9999999999,
            f"{TOKEN_URL}/user_id": 2,
            f"{TOKEN_URL}/role": "Doctor"
        }

        test_secret = "test-secret-key" # nosec B105
        token = jwt.encode(payload, test_secret, algorithm="HS256")

        return token

    @patch("utils.support_functions.jwt.decode")
    @patch("utils.support_functions.get_auth0_public_key")
    def test_verify_token_success(self, mock_get_public_key, mock_jwt_decode):
        token = self.create_valid_jwt_token()

        mock_get_public_key.return_value = "mocked-public-key"

        expected_payload = {
            f"{TOKEN_URL}/user_id": 2,
            f"{TOKEN_URL}/role": "Doctor"
        }
        mock_jwt_decode.return_value = expected_payload

        response = verify_token(token)

        self.assertEqual(response, expected_payload)
        mock_get_public_key.assert_called_once_with(token)
        mock_jwt_decode.assert_called_once()

    def test_verify_token_invalid_format(self):
        invalid_token = "invalid.token" # nosec B105

        with self.assertRaises(Exception) as context:
            verify_token(invalid_token)

        self.assertIn("Invalid token", str(context.exception))


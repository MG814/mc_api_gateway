from unittest.mock import patch
from rest_framework import status
from django.test import TestCase

from utils.support_functions import verify_token


class VerifyTokenTests(TestCase):
    @patch("requests.get")
    def test_verify_token_success(self, mock_get):
        mock_get.return_value.status_code = status.HTTP_200_OK
        mock_get.return_value.json.return_value = {"current_user_id": 1, "current_user_role": "doctor"}

        token = "valid_token"
        response = verify_token(token)

        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(response, {"current_user_id": 1, "current_user_role": "doctor"})


    @patch("requests.get")
    def test_verify_token_invalid(self, mock_get):
        mock_get.return_value.status_code = status.HTTP_401_UNAUTHORIZED

        token = "invalid_token"
        response = verify_token(token)

        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error': 'Token verification failed'})

from rest_framework import status
from django.test import TestCase, RequestFactory

from utils.support_functions import get_token


class GetTokenTests(TestCase):
    def test_get_token_success(self):
        self.factory = RequestFactory()

        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

        token = get_token(request)
        self.assertEqual(token, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9')

    def test_get_token_error(self):
        self.factory = RequestFactory()

        request = self.factory.get("/", HTTP_AUTHORIZATION="...")

        token = get_token(request)
        self.assertEqual(token.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(token.data['error'], "Authorization header missing or invalid")


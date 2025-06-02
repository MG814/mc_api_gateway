import json

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch


class AddressGatewayViewTests(APITestCase):
    def setUp(self) -> None:
        self.address_url = reverse("address-list")
        self.address_url_get = reverse("address-detail", kwargs={"pk": 1})
        self.address_url_update = reverse("address-update-user-address", kwargs={'pk': 1})

    @patch("api_accounts.views.verify_token")
    @patch("api_accounts.views.forward_request_to_service")
    def test_get_user_address_success(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {"current_user_id": 1}

        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = {
            "locality": "Sample Locality",
            "street": "Sample Street",
            "zip_code": "12345"
        }

        response = self.client.get(self.address_url_get, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            "locality": "Sample Locality",
            "street": "Sample Street",
            "zip_code": "12345"
        })

    @patch("api_accounts.views.verify_token")
    @patch("api_accounts.views.forward_request_to_service")
    def test_update_user_address_success(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {"current_user_id": 1}
        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = {"user": 1, "locality": "Updated Locality",
                                                               "street": "Updated Street", "zip_code": "54321"}
        response = self.client.patch(
            self.address_url_update,
            data=json.dumps(
                {"user": 1, "locality": "Updated Locality", "street": "Updated Street", "zip_code": "54321"}),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer mocktoken"
        )

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"user": 1, "locality": "Updated Locality", "street": "Updated Street", "zip_code": "54321"}
        )

    @patch("api_accounts.views.forward_request_to_service")
    @patch("api_accounts.views.verify_token")
    def test_update_user_address_not_found(self, mock_verify_token, mock_forward_request):
        mock_verify_token.return_value = {"sub": "test_user_id"}
        mock_forward_request.return_value.status_code = status.HTTP_404_NOT_FOUND

        response = self.client.patch(
            self.address_url_update,
            data=json.dumps(
                {"user": 1, "locality": "Updated Locality", "street": "Updated Street", "zip_code": "54321"}),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer mocktoken"
        )

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['message'], 'Address not found or not accessible')

    @patch("api_accounts.views.forward_request_to_service")
    @patch("api_accounts.views.verify_token")
    def test_create_user_address_success(self, mock_verify_token, mock_forward_request):
        mock_verify_token.return_value = {"sub": "test_user_id"}
        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = {"user": 1, "locality": "Sample Locality",
                                                               "street": "Sample Street", "zip_code": "12345"}

        response = self.client.post(
            self.address_url,
            data=json.dumps({"user": 1, "locality": "Sample Locality", "street": "Sample Street", "zip_code": "12345"}),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer mocktoken"
        )

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"user": 1, "locality": "Sample Locality", "street": "Sample Street", "zip_code": "12345"}
        )

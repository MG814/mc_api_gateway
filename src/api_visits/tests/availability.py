import json

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch, Mock

from core.settings import TOKEN_URL


class DoctorAvailabilityGatewayViewTests(APITestCase):
    def setUp(self) -> None:
        self.doctor_availability_url = reverse("availability-list")
        self.doctor_availability_url_get = reverse("availability-get-doctor-availabilities", kwargs={"doctor_id": 1})
        self.doctor_availability_url_get_detail = reverse('availability-detail', kwargs={"pk": 1})
        self.doctor_availability_url_update = reverse('availability-update-availabilities', kwargs={"pk": 1})

        self.doctor_availability_list_data = [{
            "doctor_id": 2,
            "date": "2024-11-26",
            "available_hours": {
                "8": False,
                "9": True,
                "10": True
            },
            "price": "100.00"
        },
            {
                "doctor_id": 2,
                "date": "2024-11-27",
                "available_hours": {
                    "8": True,
                    "9": True,
                    "10": True
                },
                "price": "100.00"
        }]

        self.doctor_availability_data = {
            "doctor_id": 2,
            "date": "2024-11-26",
            "available_hours": {
                "8": False,
                "9": True,
                "10": True
            },
            "price": "100.00"
        }

    @patch("api_visits.views.get_token")
    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_get_user_doctor_availabilities_success(self, mock_forward_request, mock_verify_token, mock_get_token):
        mock_get_token.return_value = "valid.jwt.token"
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": 2, f"{TOKEN_URL}/role": "Doctor"}
        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = self.doctor_availability_list_data

        response = self.client.get(self.doctor_availability_url_get, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.doctor_availability_list_data)

    @patch("api_visits.views.get_token")
    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_doctor_availability_detail_success(self, mock_forward_request, mock_verify_token, mock_get_token):
        mock_get_token.return_value = "valid.jwt.token"
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": 2, f"{TOKEN_URL}/role": "Doctor"}
        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = self.doctor_availability_data

        response = self.client.get(self.doctor_availability_url_get_detail, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.doctor_availability_data)

    @patch("api_visits.views.get_token")
    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_create_success(self, mock_forward_request, mock_verify_token, mock_get_token):
        mock_get_token.return_value = "valid.jwt.token"
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": 2, f"{TOKEN_URL}/role": "Doctor"}

        mock_user_response = Mock()
        mock_user_response.json.return_value = {'auth0_id': 2}

        mock_create_response = Mock()
        mock_create_response.status_code = status.HTTP_201_CREATED
        mock_create_response.json.return_value = self.doctor_availability_data

        mock_forward_request.side_effect = [mock_user_response, mock_create_response]

        response = self.client.post(self.doctor_availability_url, data=json.dumps(self.doctor_availability_data),
                                    content_type="application/json",
                                    HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, self.doctor_availability_data)

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_doctor_availability_create_unauthorized(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {'current_user_id': 1}
        mock_forward_request.return_value.status_code = status.HTTP_403_FORBIDDEN

        response = self.client.post(self.doctor_availability_url, data=json.dumps(self.doctor_availability_data),
                                    content_type="application/json",
                                    HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Unauthorized access.')

    @patch("api_visits.views.get_token")
    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_doctor_availability_update_success(self, mock_forward_request, mock_verify_token, mock_get_token):
        doctor_availability_data_updated = {
            "doctor_id": 2,
            "date": "2024-11-20",
            "available_hours": {"8": False, "9": False, "10": False},
            "price": "120.00"
        }

        mock_get_token.return_value = "valid.jwt.token"
        mock_verify_token.return_value = {f'{TOKEN_URL}/user_id': 2}

        mock_user_response = Mock()
        mock_user_response.json.return_value = {'auth0_id': 2}

        mock_update_response = Mock()
        mock_update_response.status_code = status.HTTP_200_OK

        mock_forward_request.side_effect = [mock_user_response, mock_update_response]

        response = self.client.patch(self.doctor_availability_url_update,
                                     data=json.dumps(doctor_availability_data_updated),
                                     content_type="application/json",
                                     HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Doctor availabilities updated successfully')

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_doctor_availability_update_unauthorized(self, mock_forward_request, mock_verify_token):
        doctor_availability_data_updated = {
            "doctor_id": 2,
            "date": "2024-11-20",
            "available_hours": {
                "8": False,
                "9": False,
                "10": False
            },
            "price": "120.00"
        }
        mock_verify_token.json.return_value = {f'{TOKEN_URL}/user_id': 20}
        mock_forward_request.return_value.status_code = status.HTTP_401_UNAUTHORIZED

        response = self.client.patch(self.doctor_availability_url_update,
                                     data=json.dumps(doctor_availability_data_updated),
                                     content_type="application/json",
                                     HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Unauthorized access.')

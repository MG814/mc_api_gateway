from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch

from core.settings import TOKEN_URL


class MedicalRecordsGatewayViewTests(APITestCase):
    def setUp(self) -> None:
        self.medical_records_url = reverse('medical-records-list')
        self.medical_records_get_url = reverse('medical-records-get-records', kwargs={"patient_id": 1})
        self.medical_records_detail_url = reverse('medical-records-detail', kwargs={"pk": 1})

        self.medical_records_data_list = [
            {
                'patient_id': 6,
                'doctor_id': 1,
                'title': 'test',
                'description': 'testtest',
            }
        ]

        self.medical_records_data = {
                'id': 1,
                'patient_id': 6,
                'doctor_id': 1,
                'title': 'test',
                'description': 'testtest',
            }

    @patch("api_medical_records.views.get_token")
    @patch("api_medical_records.views.verify_token")
    @patch("api_medical_records.views.forward_request_to_service")
    def test_get_user_medical_records_success(self, mock_forward_request, mock_verify_token, mock_get_token):
        mock_get_token.return_value = "valid.jwt.token"
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": 1,
                                          f"{TOKEN_URL}/role": "Doctor"}
        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = self.medical_records_data

        response = self.client.get(self.medical_records_get_url, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.medical_records_data)

    @patch("api_medical_records.views.get_token")
    @patch("api_medical_records.views.verify_token")
    @patch("api_medical_records.views.forward_request_to_service")
    def test_medical_records_detail_success(self, mock_forward_request, mock_verify_token, mock_get_token):
        mock_get_token.return_value = "valid.jwt.token"
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": 1,
                                          f"{TOKEN_URL}/role": "Doctor"}

        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = self.medical_records_data

        response = self.client.get(self.medical_records_detail_url, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.medical_records_data)

    @patch("api_medical_records.views.get_token")
    @patch("api_medical_records.views.verify_token")
    @patch("api_medical_records.views.forward_request_to_service")
    def test_medical_records_create_success(self, mock_forward_request, mock_verify_token, mock_get_token):
        mock_get_token.return_value = "valid.jwt.token"
        mock_verify_token.return_value = {f"{TOKEN_URL}/role": "Doctor"}
        mock_forward_request.return_value.status_code = status.HTTP_201_CREATED
        mock_forward_request.return_value.json.return_value = self.medical_records_data

        response = self.client.post(self.medical_records_url, data=self.medical_records_data,
                                    HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, self.medical_records_data)

from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch, Mock

from core.settings import TOKEN_URL


class VisitsGatewayViewTests(APITestCase):
    def setUp(self) -> None:
        self.visit_url = reverse("visit-list")
        self.visit_url_get_patient = reverse("visit-get-patient-visits", kwargs={"patient_id": 1})
        self.visit_url_get_doctor = reverse("visit-get-doctor-visits", kwargs={"doctor_id": 2})
        self.visit_url_get_detail = reverse("visit-detail", kwargs={"pk": 1})

        self.visits_list_data = [{
            "patient_id": 6,
            "doctor_id": 1,
            "date": "2024-12-01T10:00:00Z",
            "title": "Wizyta kontrolna"
        },
            {
                "patient_id": 6,
                "doctor_id": 1,
                "date": "2024-12-21T10:00:00Z",
                "title": "Wizyta kontrolna"
            }]

        self.visit_data = {
            "id": 3,
            "patient_id": 6,
            "doctor_id": 1,
            "date": "2024-12-21T10:00:00Z",
            "title": "Wizyta kontrolna",
            "price": 150
        }

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_get_patient_visits_success(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": "auth0|test_user_123"}

        visit_response = Mock()
        visit_response.status_code = status.HTTP_200_OK
        visit_response.json.return_value = self.visits_list_data

        patient_response = Mock()
        patient_response.status_code = status.HTTP_200_OK
        patient_response.json.return_value = {'auth0_id': 'auth0|test_user_123'}

        mock_forward_request.side_effect = [visit_response, patient_response]

        response = self.client.get(self.visit_url_get_patient, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.visits_list_data)

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_get_patient_visits_no_content(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": "auth0|test_user_123"}

        visit_response = Mock()
        visit_response.status_code = status.HTTP_200_OK
        visit_response.json.return_value = []

        patient_response = Mock()
        patient_response.status_code = status.HTTP_200_OK
        patient_response.json.return_value = {'auth0_id': 'auth0|test_user_123'}

        mock_forward_request.side_effect = [visit_response, patient_response]

        response = self.client.get(
            self.visit_url_get_patient,
            HTTP_AUTHORIZATION="Bearer mocktoken",
        )

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_get_patient_visits_unauthorized(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": "auth0|test_user_123"}

        visit_response = Mock()
        visit_response.status_code = status.HTTP_403_FORBIDDEN

        patient_response = Mock()
        patient_response.status_code = status.HTTP_200_OK
        patient_response.json.return_value = {'auth0_id': 'auth0|test_user_23'}

        mock_forward_request.side_effect = [visit_response, patient_response]

        response = self.client.get(self.visit_url_get_patient,
                                   HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], "Unauthorized access. "
                                                   "You do not have access to preview this visits.")

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_get_doctor_visits_success(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": "auth0|doctor_123", f"{TOKEN_URL}/role": "Doctor"}

        visit_response = Mock()
        visit_response.status_code = status.HTTP_200_OK
        visit_response.json.return_value = self.visits_list_data

        doctor_response = Mock()
        doctor_response.status_code = status.HTTP_200_OK
        doctor_response.json.return_value = {'auth0_id': 'auth0|doctor_123'}

        mock_forward_request.side_effect = [visit_response, doctor_response]

        response = self.client.get(self.visit_url_get_doctor, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.visits_list_data)

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_get_doctor_visits_no_content(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": "auth0|doctor_123", f"{TOKEN_URL}/role": "Doctor"}

        visit_response = Mock()
        visit_response.status_code = status.HTTP_200_OK
        visit_response.json.return_value = []

        doctor_response = Mock()
        doctor_response.status_code = status.HTTP_200_OK
        doctor_response.json.return_value = {'auth0_id': 'auth0|doctor_123'}

        mock_forward_request.side_effect = [visit_response, doctor_response]

        response = self.client.get(
            self.visit_url_get_doctor,
            HTTP_AUTHORIZATION="Bearer mocktoken",
        )

        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_get_doctor_visits_unauthorized(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": 2, f"{TOKEN_URL}/role": "Doctor"}
        mock_forward_request.return_value.status_code = status.HTTP_403_FORBIDDEN

        response = self.client.get(self.visit_url_get_doctor, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], "Unauthorized access. "
                                                   "You do not have access to preview this visits.")

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_visit_detail_success(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": "auth0|test_user_123"}

        visit_response = Mock()
        visit_response.status_code = status.HTTP_200_OK
        visit_response.json.return_value = self.visit_data

        doctor_response = Mock()
        doctor_response.status_code = status.HTTP_200_OK
        doctor_response.json.return_value = {'auth0_id': 'auth0|doctor_123'}

        patient_response = Mock()
        patient_response.status_code = status.HTTP_200_OK
        patient_response.json.return_value = {'auth0_id': 'auth0|test_user_123'}

        mock_forward_request.side_effect = [visit_response, doctor_response, patient_response]

        response = self.client.get(self.visit_url_get_detail, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.visit_data)

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_visit_detail_unauthorized(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": "auth0|test_user_123"}

        visit_response = Mock()
        visit_response.status_code = status.HTTP_403_FORBIDDEN

        doctor_response = Mock()
        doctor_response.status_code = status.HTTP_200_OK
        doctor_response.json.return_value = {'auth0_id': 'auth0|doctor_123'}

        patient_response = Mock()
        patient_response.status_code = status.HTTP_200_OK
        patient_response.json.return_value = {'auth0_id': 'auth0|test_user_13'}

        mock_forward_request.side_effect = [visit_response, doctor_response, patient_response]

        response = self.client.get(self.visit_url_get_detail, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 3)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Unauthorized access. '
                                                   'You do not have access to preview this visit.')

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_visit_create_success(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/role": "Doctor"}
        mock_forward_request.return_value.status_code = status.HTTP_201_CREATED
        mock_forward_request.return_value.json.return_value = self.visit_data

        response = self.client.post(self.visit_url, data=self.visit_data, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, self.visit_data)

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_visit_delete_success(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {f"{TOKEN_URL}/role": "Doctor"}
        mock_forward_request.return_value.status_code = status.HTTP_204_NO_CONTENT

        response = self.client.delete(self.visit_url, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

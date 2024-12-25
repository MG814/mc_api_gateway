from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch


class VisitsGatewayViewTests(APITestCase):
    def setUp(self) -> None:
        self.visit_url = reverse("visit-list")
        self.visit_url_get = reverse("visit-get-patient-visits", kwargs={"patient_id": 1})
        self.visit_url_get_login = reverse("visit-get-login-user-visits")
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
    def test_get_user_visits_success(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {"current_user_id": 1,
                                          "current_user_role": "Doctor"}

        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = self.visits_list_data

        response = self.client.get(self.visit_url_get, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.visits_list_data)

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_get_user_visits_no_content(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {"current_user_id": 1,
                                          "current_user_role": "Doctor"}
        mock_forward_request.return_value.status_code = status.HTTP_204_NO_CONTENT
        mock_forward_request.return_value.json.return_value = []

        response = self.client.get(
            self.visit_url_get,
            HTTP_AUTHORIZATION="Bearer mocktoken",
        )

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, [])

    @patch("api_visits.views.forward_request_to_service")
    def test_get_user_visits_unauthorized(self, mock_forward_request):
        mock_forward_request.return_value.status_code = status.HTTP_401_UNAUTHORIZED

        response = self.client.get(self.visit_url_get, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Unauthorized access.')

    @patch("api_visits.views.forward_request_to_service")
    def test_get_login_user_visits_success(self, mock_forward_request):
        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = self.visits_list_data

        response = self.client.get(self.visit_url_get_login, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.visits_list_data)

    @patch("api_visits.views.forward_request_to_service")
    def test_get_login_user_visits_no_content(self, mock_forward_request):
        mock_forward_request.return_value.status_code = status.HTTP_204_NO_CONTENT
        mock_forward_request.return_value.json.return_value = []

        response = self.client.get(
            self.visit_url_get_login,
            HTTP_AUTHORIZATION="Bearer mocktoken",
        )

        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, [])

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_visit_detail_success(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {"current_user_id": 1}

        mock_forward_request.return_value.status_code = status.HTTP_200_OK
        mock_forward_request.return_value.json.return_value = self.visit_data

        response = self.client.get(self.visit_url_get_detail, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.visit_data)

    @patch("api_visits.views.verify_token")
    @patch("api_visits.views.forward_request_to_service")
    def test_visit_detail_unauthorized(self, mock_forward_request, mock_verify_token):
        mock_verify_token.return_value = {"current_user_id": 2}

        mock_forward_request.return_value.status_code = status.HTTP_401_UNAUTHORIZED

        response = self.client.get(self.visit_url_get_detail, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_verify_token.call_count, 1)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Unauthorized access.')

    @patch("api_visits.views.forward_request_to_service")
    def test_visit_create_success(self, mock_forward_request):
        mock_forward_request.return_value.status_code = status.HTTP_201_CREATED
        mock_forward_request.return_value.json.return_value = self.visit_data

        response = self.client.post(self.visit_url, data=self.visit_data, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, self.visit_data)

    @patch("api_visits.views.forward_request_to_service")
    def test_visit_delete_success(self, mock_forward_request):

        mock_forward_request.return_value.status_code = status.HTTP_204_NO_CONTENT

        response = self.client.delete(self.visit_url, HTTP_AUTHORIZATION="Bearer mocktoken")

        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, Mock

from core.settings import TOKEN_URL


class UpdateUserGatewayViewTest(APITestCase):

    def setUp(self):
        self.update_user_url = reverse('update-user-update-user', kwargs={'pk': 1})


    @patch('api_accounts.views.forward_request_to_service')
    @patch('api_accounts.views.verify_token')
    def test_update_user_success(self, mock_verify_token, mock_forward_request):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": "auth0|user_123"}

        user_response = Mock()
        user_response.status_code = status.HTTP_200_OK
        user_response.json.return_value = {'auth0_id': "auth0|user_123"}

        mock_patch_response = Mock()
        mock_patch_response.status_code = status.HTTP_200_OK
        mock_patch_response.json.return_value = {'message': 'User updated.'}

        mock_forward_request.side_effect = [user_response, mock_patch_response]

        self.user_updated_data = {'name': 'New Name'}

        response = self.client.patch(self.update_user_url, data=self.user_updated_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_forward_request.call_count, 2)
        self.assertEqual(response.data, {'message': 'User updated.'})

    @patch('api_accounts.views.forward_request_to_service')
    @patch('api_accounts.views.verify_token')
    def test_update_user_unauthorized(self, mock_verify_token, mock_forward_request):
        mock_verify_token.return_value = {f"{TOKEN_URL}/user_id": "auth0|user_123"}

        mock_get_response = Mock()
        mock_get_response.json.return_value = {'auth0_id': 'different_user'}
        mock_forward_request.return_value = mock_get_response

        response = self.client.patch(self.update_user_url, {'name': 'New Name'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(mock_forward_request.call_count, 1)
        self.assertEqual(response.data['message'], "Unauthorized access. You are trying to update another user's data.")


class UserGatewayViewTest(APITestCase):

    def setUp(self):
        self.user_detail_url = reverse('user-detail-user-detail', kwargs={'pk': 1})

    @patch('api_accounts.views.forward_request_to_service')
    @patch('api_accounts.views.verify_token')
    def test_user_detail_success(self, mock_verify_token, mock_forward_request):
        mock_verify_token.return_value = True

        mock_response = Mock()
        mock_response.json.return_value = {'id': 1, 'name': 'Test User', 'email': 'test@example.com'}
        mock_response.status_code = status.HTTP_200_OK
        mock_forward_request.return_value = mock_response

        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'id': 1, 'name': 'Test User', 'email': 'test@example.com'})

    @patch('api_accounts.views.forward_request_to_service')
    @patch('api_accounts.views.verify_token')
    def test_user_detail_not_found(self, mock_verify_token, mock_forward_request):
        mock_verify_token.return_value = True

        mock_response = Mock()
        mock_response.json.return_value = {'error': 'User not found'}
        mock_response.status_code = status.HTTP_404_NOT_FOUND
        mock_forward_request.return_value = mock_response

        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'User not found'})
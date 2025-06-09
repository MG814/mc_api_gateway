from unittest.mock import patch, Mock
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class CallbackViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.callback_url = reverse('callback')

    def test_no_code_returns_400(self):
        response = self.client.get(self.callback_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No authorization code')

    @patch('requests.post')
    def test_auth0_error_returns_error(self, mock_post):
        mock_post.return_value.status_code = status.HTTP_400_BAD_REQUEST
        mock_post.return_value.json.return_value = {'error'}

        response = self.client.get(self.callback_url, {'code': 'bad_code'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Failed to exchange code for token')

    @patch('api_token_jwt.views.forward_request_to_service')
    @patch('api_token_jwt.views.verify_token')
    @patch('requests.get')
    @patch('requests.post')
    def test_new_user_success(self, mock_post, mock_get, mock_verify, mock_forward):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {'access_token': 'valid.token.here'}
        )

        mock_get.return_value = Mock(status_code=404)

        mock_verify.return_value = {
            'https://user-info/user_id': 'auth0|123',
            'https://user-info/user_email': 'test@test.com'
        }

        response = self.client.get(self.callback_url, {'code': 'valid_code'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        mock_forward.assert_called_once()

    @patch('api_token_jwt.views.verify_token')
    @patch('requests.get')
    @patch('requests.post')
    def test_existing_user_success(self, mock_post, mock_get, mock_verify):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'valid.token.here'}

        mock_get.return_value = Mock(status_code=200)

        mock_verify.return_value = {
            'https://user-info/user_id': 'auth0|123'
        }

        response = self.client.get(self.callback_url, {'code': 'valid_code'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)

    @patch('api_token_jwt.views.verify_token')
    @patch('requests.get')
    @patch('requests.post')
    def test_invalid_token_returns_400(self, mock_post, mock_get, mock_verify):
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {'access_token': 'invalid.token.'}
        )

        mock_get.return_value = Mock(status_code=200)
        mock_verify.return_value = {'https://user-info/user_id': 'auth0|123'}

        response = self.client.get(self.callback_url, {'code': 'valid_code'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Auth0 returned invalid access_token')
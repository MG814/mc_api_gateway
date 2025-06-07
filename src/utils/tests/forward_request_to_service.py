from unittest.mock import patch
from rest_framework import status
from django.test import TestCase

from utils.support_functions import forward_request_to_service


class ForwardRequestToServiceTests(TestCase):
    def setUp(self) -> None:
        self.test_token = "test_valid_token" # nosec B105

    @patch("requests.get")
    def test_request_get_success(self, mock_get):
        mock_get.return_value.status_code = status.HTTP_200_OK
        url = 'testurl'
        data = {'data': 'testtest'}

        response = forward_request_to_service(url, data, self.test_token, method='get')

        self.assertEqual(mock_get.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("requests.post")
    def test_request_post_success(self, mock_post):
        mock_post.return_value.status_code = status.HTTP_201_CREATED
        url = 'testurl'
        data = {'data': 'testtest'}

        response = forward_request_to_service(url, data, self.test_token, method='post')

        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("requests.put")
    def test_request_put_success(self, mock_put):
        mock_put.return_value.status_code = status.HTTP_200_OK
        url = 'testurl'
        data = {'data': 'testtest'}

        response = forward_request_to_service(url, data, self.test_token, method='put')

        self.assertEqual(mock_put.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("requests.patch")
    def test_request_patch_success(self, mock_patch):
        mock_patch.return_value.status_code = status.HTTP_200_OK
        url = 'testurl'
        data = {'data': 'testtest'}

        response = forward_request_to_service(url, data, self.test_token, method='patch')

        self.assertEqual(mock_patch.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("requests.delete")
    def test_request_delete_success(self, mock_delete):
        mock_delete.return_value.status_code = status.HTTP_204_NO_CONTENT
        url = 'testurl'
        data = {'data': 'testtest'}

        response = forward_request_to_service(url, data, self.test_token, method='delete')

        self.assertEqual(mock_delete.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_method_not_allowed(self):
        url = 'testurl'
        data = {'data': 'testtest'}

        response = forward_request_to_service(url, data, self.test_token, method='p')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data, {'error': f'Unsupported method p'})
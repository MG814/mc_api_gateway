from unittest.mock import patch, Mock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import requests


class StatisticGatewayViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.statistic = reverse('statistic')

    @patch('requests.post')
    def test_success(self, mock_post):
        mock_post.return_value = Mock(
            status_code=status.HTTP_200_OK,
            json=lambda: {"data": "success"}
        )

        response = self.client.post(self.statistic, {"query": "test"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"data": "success"})

    @patch('requests.post')
    def test_error_response(self, mock_post):
        mock_post.return_value = Mock(
            status_code=status.HTTP_400_BAD_REQUEST,
            json=lambda: {"error": "bad request"}
        )

        response = self.client.post(self.statistic, {"query": "test"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('requests.post')
    def test_connection_error(self, mock_post):
        mock_post.side_effect = requests.ConnectionError("Connection failed")

        response = self.client.post(self.statistic, {"query": "test"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
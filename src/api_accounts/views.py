import json
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import GenericViewSet

from utils.support_functions import verify_token, forward_request_to_service, get_token


@method_decorator(csrf_exempt, name='dispatch')
class LoginGatewayView(GenericViewSet):

    def create(self, request):
        try:
            login_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        accounts_url = 'http://web-accounts:8100/login/create-token/'

        username = login_data.get('username')
        password = login_data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Missing username or password'}, status=400)

        response = forward_request_to_service(accounts_url, login_data, method='POST')

        return JsonResponse(response.json(), status=response.status_code)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterGatewayView(GenericViewSet):

    def create(self, request):
        try:
            register_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        if not register_data.get('first_name') or not register_data.get('last_name'):
            return JsonResponse({'error': 'First and last name are required'}, status=400)
        elif not register_data.get('email') or not register_data.get('phone'):
            return JsonResponse({'error': 'email and phone are required'}, status=400)

        accounts_url = 'http://web-accounts:8100/register/'

        response = forward_request_to_service(accounts_url, register_data, method='post')
        return JsonResponse(response.json(), status=response.status_code)


class UserAddressGatewayView(GenericViewSet):
    @action(methods=['GET'], detail=False, url_path='my')
    def get_user_address(self, request):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get('current_user_id')

        address_service_url = f'http://web-accounts:8100/address/{user_id}/'
        address_response = forward_request_to_service(address_service_url, token=token, method='get')
        address_data = address_response.json()

        if address_response.status_code == status.HTTP_200_OK:
            return Response(address_data, status=status.HTTP_200_OK)
        else:
            return Response(address_data, status=address_response.status_code)

    @action(methods=['PATCH'], detail=True, url_path='my/update')
    def update_user_address(self, request, pk=None):
        token = get_token(request)
        token_data = verify_token(token)
        user_id = token_data.get('current_user_id')
        address_url = f'http://web-accounts:8100/address/{pk}/'
        address_response = forward_request_to_service(address_url, token=token, method='get')

        if address_response.status_code != status.HTTP_200_OK:
            return Response({'message': 'Address not found or not accessible'}, status=status.HTTP_404_NOT_FOUND)

        address_data = address_response.json()

        if address_data.get('user') != user_id:
            return Response({'message': 'Unauthorized to update this address'}, status=status.HTTP_403_FORBIDDEN)

        update_response = forward_request_to_service(address_url, request.data, token, method='patch')

        if update_response.status_code == status.HTTP_200_OK:
            return Response(update_response.json(), status=status.HTTP_200_OK)
        else:
            return Response(update_response.json(), status=update_response.status_code)

    def create(self, request):
        token = get_token(request)

        verify_token(token)
        user_service_url = f'http://web-accounts:8100/address/'

        address_response = forward_request_to_service(url=user_service_url, data=request.data, token=token, method='post')
        response_data = address_response.json()

        if address_response.status_code == status.HTTP_200_OK:
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(response_data, status=address_response.status_code)

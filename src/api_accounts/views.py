from django.http import JsonResponse
from django.shortcuts import redirect

from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from utils.support_functions import verify_token, forward_request_to_service, get_token

from core.settings import ACCOUNTS_SERVICE_URL, TOKEN_URL


class LoginGatewayView(APIView):

    def get(self, request, *args, **kwargs):
        accounts_url = f'{ACCOUNTS_SERVICE_URL}/login/'

        response = forward_request_to_service(accounts_url, method='get')
        return JsonResponse(response.json(), status=response.status_code)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        accounts_logout_url = f"{ACCOUNTS_SERVICE_URL}/logout/"

        response = forward_request_to_service(accounts_logout_url, method='get')
        logout_url = response.json()['logout_url']
        return redirect(logout_url)


class RegisterGatewayView(APIView):

    def get(self, request, *args, **kwargs):
        accounts_url = f'{ACCOUNTS_SERVICE_URL}/register/'

        response = forward_request_to_service(accounts_url, method='get')
        return JsonResponse(response.json(), status=response.status_code)


class UpdateUserGatewayView(GenericViewSet):
    @action(methods=['PATCH'], detail=True, url_path='update-user')
    def update_user(self, request, pk=None):
        token = get_token(request)
        token_data=verify_token(token)
        user_id = token_data.get(f'{TOKEN_URL}/user_id')

        accounts_url = f"{ACCOUNTS_SERVICE_URL}/users/{pk}/"
        response = forward_request_to_service(url=accounts_url, method='get')

        if user_id == response.json().get('auth0_id'):
            accounts_url = f"{ACCOUNTS_SERVICE_URL}/update-user/{pk}/"
            response = forward_request_to_service(url=accounts_url, data=request.data, method='patch')
            return Response(response.json(), status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED) #poprawić message


class UserGatewayView(GenericViewSet):
    @action(methods=['GET'], detail=True, url_path='user-detail')
    def user_detail(self, request, pk=None):
        token = get_token(request)
        verify_token(token)

        accounts_url = f"{ACCOUNTS_SERVICE_URL}/users/{pk}/"

        response = forward_request_to_service(url=accounts_url, method='get')

        return Response(response.json(), status=response.status_code)


class UserAddressGatewayView(GenericViewSet):

    def retrieve(self, request, pk=None):
        token = get_token(request)

        verify_token(token)

        address_service_url = f'{ACCOUNTS_SERVICE_URL}/address/{pk}/'
        address_response = forward_request_to_service(address_service_url, token=token, method='get')
        address_data = address_response.json()

        if address_response.status_code == status.HTTP_200_OK:
            return Response(address_data, status=status.HTTP_200_OK)
        else:
            return Response(status=address_response.status_code)


    @action(methods=['PATCH'], detail=True, url_path='update')
    def update_user_address(self, request, pk=None):
        token = get_token(request)
        verify_token(token)

        address_url = f'{ACCOUNTS_SERVICE_URL}/address/{pk}/'
        address_response = forward_request_to_service(address_url, token=token, method='get')

        if address_response.status_code != status.HTTP_200_OK:
            return Response({'message': 'Address not found or not accessible'}, status=status.HTTP_404_NOT_FOUND)

        update_response = forward_request_to_service(address_url, request.data, token, method='patch')

        if update_response.status_code == status.HTTP_200_OK:
            return Response(update_response.json(), status=status.HTTP_200_OK)
        else:
            return Response(update_response.json(), status=update_response.status_code)

    def create(self, request, *args, **kwargs):
        token = get_token(request)

        verify_token(token)

        user_service_url = f'{ACCOUNTS_SERVICE_URL}/address/'

        address_response = forward_request_to_service(url=user_service_url, data=request.data, token=token,
                                                      method='post')
        address_data = address_response.json()
        if address_response.status_code == status.HTTP_200_OK:
            return Response(address_data, status=status.HTTP_200_OK)
        else:
            return Response(address_data, status=address_response.status_code)

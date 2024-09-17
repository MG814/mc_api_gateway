import json
import requests
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


@method_decorator(csrf_exempt, name='dispatch')
class LoginGatewayView(View):
    def post(self, request):
        try:
            login_data = json.loads(request.body)  # Pobranie danych w formacie JSON
            print(login_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # Adres mikroserwisu profiles
        accounts_url = 'http://web-accounts:8100/login/create-token/'

        # Sprawdzenie, czy dane logowania zawierają wymagane pola (np. username i password)
        username = login_data.get('username')
        password = login_data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Missing username or password'}, status=400)

        # Przekazanie danych logowania do mikroserwisu profiles
        response = requests.post(accounts_url, json=login_data)

        # Zwrócenie odpowiedzi z mikroserwisu (token JWT) do użytkownika
        return JsonResponse(response.json(), status=response.status_code)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterGatewayView(View):
    def post(self, request):
        try:
            register_data = json.loads(request.body)  # Pobranie danych w formacie JSON
            print(register_data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # Sprawdzanie, czy wszystkie wymagane pola są wypełnione
        if not register_data.get('first_name') or not register_data.get('last_name'):
            return JsonResponse({'error': 'First and last name are required'}, status=400)
        elif not register_data.get('email') or not register_data.get('phone'):
            return JsonResponse({'error': 'email and phone are required'}, status=400)

        # Adres mikroserwisu profiles
        accounts_url = 'http://web-accounts:8100/register/'

        # Przekazanie danych logowania do mikroserwisu profiles
        response = requests.post(accounts_url, json=register_data)

        # Zwrócenie odpowiedzi z mikroserwisu (token JWT) do użytkownika
        return JsonResponse(response.json(), status=response.status_code)


class UserAddressGatewayView(APIView):

    def get(self, request):

        # Pobieramy token JWT z nagłówka Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)

        # Sprawdzamy, czy nagłówek Authorization istnieje
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)

        # Pobieramy token po słowie 'Bearer'
        token = auth_header.split(' ')[1]

        # Adres mikroserwisu user-service
        user_service_url = 'http://web-accounts:8100/user/verify-token/'

        # Przekazujemy żądanie do mikroserwisu user-service w celu weryfikacji tokena
        headers = {
            'Authorization': f'Bearer {token}'  # Przekazujemy token JWT do mikroserwisu
        }

        try:
            # Wysyłamy żądanie GET do mikroserwisu, aby zweryfikować token
            response = requests.get(user_service_url, headers=headers)
            response_data = response.json()

            # Sprawdzamy status odpowiedzi mikroserwisu
            if response.status_code == 200:
                # Token zweryfikowany, możemy teraz wysłać żądanie o adres użytkownika
                address_service_url = 'http://web-accounts:8100/user/address/'
                address_response = requests.get(address_service_url, headers=headers)
                address_data = address_response.json()

                if address_response.status_code == 200:
                    return Response(address_data, status=status.HTTP_200_OK)
                else:
                    return Response(address_data, status=address_response.status_code)
            else:
                # Mikroserwis zwrócił błąd przy weryfikacji tokena
                return Response(response_data, status=response.status_code)

        except requests.exceptions.RequestException as e:
            # Obsługa błędów połączenia z mikroserwisem
            return Response({'error': 'Service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

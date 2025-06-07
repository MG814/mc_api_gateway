from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
import requests

from http import HTTPStatus

from core import settings
from utils.support_functions import verify_token, forward_request_to_service


class CallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Brak kodu autoryzacyjnego"}, status=status.HTTP_400_BAD_REQUEST)

        # Wymiana kodu na token
        token_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.AUTH0_CALLBACK_URL,
            "audience": settings.AUTH0_AUDIENCE,
            "scope": "openid profile email",
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(token_url, json=payload, headers=headers, timeout=10)

        # Obsługa błędów z Auth0
        if response.status_code != status.HTTP_200_OK:
            error_data = response.json()
            return Response(
                {"error": "Nie udało się wymienić kodu na token", "details": error_data},
                status=response.status_code,
            )

        tokens = response.json()
        access_token = tokens.get("access_token")

        token_data = verify_token(access_token)
        auth0_user_id = token_data.get('https://user-info/user_id')

        accounts_get_url = f"http://web-accounts:8100/users/{auth0_user_id}/"
        try:
            get_response = requests.get(accounts_get_url, timeout=10)
            if get_response.status_code == status.HTTP_404_NOT_FOUND:
                registration = True
            elif get_response.status_code == HTTPStatus.OK:
                registration = False
            else:
                registration = False
        except requests.exceptions.RequestException:
            return Response({'error': 'Błąd połączenia z mikroserwisem accounts'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if registration:
            user_data = {"user_id": auth0_user_id,
                         "username": token_data.get('https://user-info/user_name'),
                         "email": token_data.get('https://user-info/user_email'),
                         "name": token_data.get('https://user-info/name'),
                         "surname": token_data.get('https://user-info/surname'),
                         "phone": token_data.get('https://user-info/phone'),
                         "role": token_data.get('https://user-info/role'),
                         "specialization": token_data.get('https://user-info/specialization')
                         }

            accounts_url = 'http://web-accounts:8100/register/'
            forward_request_to_service(accounts_url, user_data, method='post')

        if access_token and access_token.split(".")[-1] != "":
            return Response(tokens)
        else:
            return Response(
                {"error": "Auth0 zwróciło nieprawidłowy access_token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
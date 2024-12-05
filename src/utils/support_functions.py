import requests
from rest_framework.response import Response
from rest_framework import status


def verify_token(token):
    """
    Funkcja do weryfikacji tokena JWT w mikroserwisie accounts.
    Zwraca dane użytkownika, jeśli token jest prawidłowy.
    """
    verify_token_url = 'http://web-accounts:8100/users/verify-token/'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(verify_token_url, headers=headers)
        if response.status_code == status.HTTP_200_OK:
            return response.json()
        else:
            return Response({'error': 'Token verification failed'}, status=status.HTTP_401_UNAUTHORIZED)
    except requests.exceptions.RequestException:
        return Response({'error': 'Service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def forward_request_to_service(url, data=None, token=None, role=None, method=None):
    """
    Funkcja do przekazywania żądań do mikroserwisów obsługująca różne typy żądań HTTP.
    """
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if role:
        headers['role'] = role

    try:
        # Sprawdź, który typ żądania wykonać
        if method.lower() == 'get':
            response = requests.get(url, headers=headers, params=data)
        elif method.lower() == 'post':
            response = requests.post(url, json=data, headers=headers)
        elif method.lower() == 'put':
            response = requests.put(url, json=data, headers=headers)
        elif method.lower() == 'patch':
            response = requests.patch(url, json=data, headers=headers)
        elif method.lower() == 'delete':
            response = requests.delete(url, headers=headers)
        else:
            return Response({'error': f'Unsupported method {method}'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return response

    except requests.exceptions.RequestException:
        return Response({'error': 'Service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def get_token(request):
    # Pobieramy token JWT z nagłówka Authorization
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        return token

    return Response({'error': 'Authorization header missing or invalid'},
                    status=status.HTTP_401_UNAUTHORIZED)

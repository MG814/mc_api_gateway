from rest_framework.response import Response
from rest_framework import status
import requests
import jwt
from jwt.algorithms import RSAAlgorithm
from django.conf import settings


def get_auth0_public_key(token):
    jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(jwks_url, timeout=10)
    jwks = response.json()

    unverified_header = jwt.get_unverified_header(token)
    token_kid = unverified_header.get('kid')

    key = None
    for k in jwks["keys"]:
        if k.get("kid") == token_kid:
            key = k
            break

    if key is None:
        raise Exception("Nie znaleziono klucza o odpowiednim kid w JWKS.")

    public_key = RSAAlgorithm.from_jwk(key)
    return public_key


def verify_token(token):
    try:
        public_key = get_auth0_public_key(token)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/",
            options={"verify_iat": True},
            leeway=10
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError as e:
        raise Exception("Invalid token: " + str(e))


def forward_request_to_service(url, data=None, token=None, role=None, method=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if role:
        headers['role'] = role

    try:
        if method.lower() == 'get':
            response = requests.get(url, headers=headers, params=data, timeout=10)
        elif method.lower() == 'post':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.lower() == 'put':
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method.lower() == 'patch':
            response = requests.patch(url, json=data, headers=headers, timeout=10)
        elif method.lower() == 'delete':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return Response({'error': f'Unsupported method {method}'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return response

    except requests.exceptions.RequestException:
        return Response({'error': 'Service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


def get_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        return token

    return Response({'error': 'Authorization header missing or invalid'},
                    status=status.HTTP_401_UNAUTHORIZED)


def get_management_token():
    token_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": settings.AUTH0_CLIENT_ID,
        "client_secret": settings.AUTH0_CLIENT_SECRET,
        "audience": f"https://{settings.AUTH0_DOMAIN}/api/v2/"
    }
    response = requests.post(token_url, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("access_token")

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import GenericViewSet

from utils.support_functions import verify_token, forward_request_to_service, get_token

from core.settings import VISITS_SERVICE_URL, PAYMENTS_SERVICE_URL, TOKEN_URL, ACCOUNTS_SERVICE_URL


class VisitGatewayViewSet(GenericViewSet):
    @action(methods=['GET'], detail=False, url_path='patients/(?P<patient_id>[\w\-]+)')
    def get_patient_visits(self, request, patient_id=None):
        token = get_token(request)
        token_data = verify_token(token)

        user_id = token_data.get(f'{TOKEN_URL}/user_id')
        role = token_data.get(f'{TOKEN_URL}/role')

        service_url = f'{VISITS_SERVICE_URL}/visits/patient/{patient_id}/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        accounts_url = f"{ACCOUNTS_SERVICE_URL}/users/{patient_id}/"
        response = forward_request_to_service(url=accounts_url, method='get')
        patient_auth0_id = response.json().get('auth0_id')

        if patient_auth0_id == user_id or role == 'Doctor':
            if response.status_code == status.HTTP_200_OK:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(data, status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['GET'], detail=False, url_path='doctors/(?P<doctor_id>[\w-]+)')
    def get_doctor_visits(self, request, doctor_id=None):
        token = get_token(request)
        token_data = verify_token(token)

        user_id = token_data.get(f'{TOKEN_URL}/user_id')
        role = token_data.get(f'{TOKEN_URL}/role')

        service_url = f'{VISITS_SERVICE_URL}/visits/doctor/{doctor_id}/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        accounts_url = f"{ACCOUNTS_SERVICE_URL}/users/{doctor_id}/"
        response = forward_request_to_service(url=accounts_url, method='get')
        doctor_auth0_id = response.json().get('auth0_id')

        if doctor_auth0_id == user_id and role == 'Doctor':
            if response.status_code == status.HTTP_200_OK:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(data, status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get(f'{TOKEN_URL}/user_id')
        doctor_id = request.data.get('doctor_id')
        patient_id = request.data.get('patient_id')

        service_url = f'{VISITS_SERVICE_URL}/visits/{pk}/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        accounts_url = f"{ACCOUNTS_SERVICE_URL}/users/{doctor_id}/"
        response = forward_request_to_service(url=accounts_url, method='get')
        doctor_auth0_id = response.json().get('auth0_id')

        accounts_url = f"{ACCOUNTS_SERVICE_URL}/users/{patient_id}/"
        response = forward_request_to_service(url=accounts_url, method='get')
        patient_auth0_id = response.json().get('auth0_id')

        if user_id == doctor_auth0_id or user_id == patient_auth0_id:
            if response.status_code == status.HTTP_200_OK:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        token = get_token(request)
        token_data = verify_token(token)

        current_user_role = token_data.get(f'{TOKEN_URL}/role')

        service_url = f'{VISITS_SERVICE_URL}/visits/'
        response = forward_request_to_service(service_url, request.data, token, role=current_user_role, method='post')

        if response.status_code == status.HTTP_201_CREATED:
            payment_data = {'price': request.data.get('price'), 'name': request.data.get('title'),
                            'visit_id': response.json()['id']}
            stripe_url = f'{PAYMENTS_SERVICE_URL}/create-checkout-session/'
            stripe_response = forward_request_to_service(stripe_url, data=payment_data, token=token, method='post')

            return Response(stripe_response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)

    def delete(self, request, pk=None):
        token = get_token(request)
        token_data = verify_token(token)

        current_user_role = token_data.get(f'{TOKEN_URL}/role')
        visits_service_url = f'{VISITS_SERVICE_URL}/visits/delete/{pk}/'
        visit_response = forward_request_to_service(visits_service_url, token, role=current_user_role, method='delete')

        if visit_response.status_code == status.HTTP_204_NO_CONTENT:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            try:
                visit_data = visit_response.json()
                message = visit_data.get('message')
            except ValueError:
                message = "An error occurred, but no additional message provided."

            return Response({"message": message}, status=visit_response.status_code)


class DoctorAvailabilityGatewayViewSet(GenericViewSet):

    @action(methods=['GET'], detail=False, url_path='doctors/(?P<doctor_id>\d+)/availability')
    def get_doctor_availabilities(self, request, doctor_id=None):
        token = get_token(request)

        verify_token(token)

        service_url = f'{VISITS_SERVICE_URL}/doctor-availabilities/doctors/{doctor_id}/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        if response.status_code == status.HTTP_200_OK:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(data, status=response.status_code)

    def retrieve(self, request, pk=None):
        token = get_token(request)

        verify_token(token)

        service_url = f'{VISITS_SERVICE_URL}/doctor-availabilities/{pk}/'
        response = forward_request_to_service(service_url, token=token, method='get')

        data = response.json()

        if response.status_code == status.HTTP_200_OK:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(data, status=response.status_code)

    def create(self, request, *args, **kwargs):
        token = get_token(request)

        token_data = verify_token(token)

        current_user_role = token_data.get(f'{TOKEN_URL}/role')
        user_id = token_data.get(f'{TOKEN_URL}/user_id')

        service_url = f'{VISITS_SERVICE_URL}/doctor-availabilities/'

        accounts_url = f"{ACCOUNTS_SERVICE_URL}/users/{request.data.get('doctor_id')}/"
        response = forward_request_to_service(url=accounts_url, method='get')

        if user_id == response.json().get('auth0_id'):
            response = forward_request_to_service(service_url, request.data, token, role=current_user_role,
                                                  method='post')
            if response.status_code == status.HTTP_201_CREATED:
                return Response(response.json(), status=status.HTTP_201_CREATED)
            else:
                return Response(response.json(), status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['PATCH'], detail=True, url_path='update-availabilities')
    def update_availabilities(self, request, pk=None):
        token = get_token(request)
        token_data = verify_token(token)
        user_id = token_data.get(f'{TOKEN_URL}/user_id')

        service_url = f'{VISITS_SERVICE_URL}/doctor-availabilities/{pk}/'

        accounts_url = f"{ACCOUNTS_SERVICE_URL}/users/{request.data.get('doctor_id')}/"
        response = forward_request_to_service(url=accounts_url, method='get')

        if user_id == response.json().get('auth0_id'):
            response = forward_request_to_service(service_url, data=request.data, token=token, method='patch')
            if response.status_code == status.HTTP_200_OK:
                return Response({'message': 'Doctor availabilities updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(response.json(), status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_403_FORBIDDEN)

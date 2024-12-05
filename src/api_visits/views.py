from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import GenericViewSet

from utils.support_functions import verify_token, forward_request_to_service, get_token


class VisitGatewayViewSet(GenericViewSet):
    @action(methods=['GET'], detail=False, url_path='patients/(?P<patient_id>\d+)/visits')
    def get_patient_visits(self, request, patient_id=None):
        token = get_token(request)
        token_data = verify_token(token)

        user_id = token_data.get('current_user_id')
        role = token_data.get('role')

        service_url = f'http://web-visits:8600/visits/patient/{patient_id}/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        if patient_id == user_id or role == 'Doctor':
            if response.status_code == status.HTTP_200_OK:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(data, status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['GET'], detail=False, url_path='patients/my/visits')
    def get_login_user_visits(self, request):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get('current_user_id')

        service_url = f'http://web-visits:8600/visits/patient/{user_id}/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        if response.status_code == status.HTTP_200_OK:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(data, status=response.status_code)

    def retrieve(self, request, pk=None):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            return Response({'error': 'Authorization header missing or invalid'},
                            status=status.HTTP_401_UNAUTHORIZED)

        token_data = verify_token(token)
        user_id = token_data.get('current_user_id')

        service_url = f'http://web-visits:8600/visits/{pk}/'
        response = forward_request_to_service(service_url, token=token, method='get')

        data = response.json()

        if user_id == data.get('patient_id') or user_id == data.get('doctor_id'):
            if response.status_code == status.HTTP_200_OK:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        token = get_token(request)
        token_data = verify_token(token)

        current_user_role = token_data.get('current_user_role')

        service_url = 'http://web-visits:8600/visits/'
        response = forward_request_to_service(service_url, request.data, token, role=current_user_role, method='post')

        if response.status_code == status.HTTP_201_CREATED:
            payment_data = {'price': request.data.get('price'), 'name': request.data.get('title'),
                            'visit_id': response.json()['id']}
            stripe_url = 'http://web-payments:8500/create-checkout-session/'
            stripe_response = forward_request_to_service(stripe_url, data=payment_data, token=token, method='post')

            return Response(stripe_response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)

    def delete(self, request, pk=None):
        token = get_token(request)
        token_data = verify_token(token)

        current_user_role = token_data.get('current_user_role')
        visits_service_url = f'http://web-visits:8600/visits/delete/{pk}/'
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

        service_url = f'http://web-visits:8600/doctor-availabilities/doctor/{doctor_id}/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        if response.status_code == status.HTTP_200_OK:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(data, status=response.status_code)

    @action(methods=['GET'], detail=False, url_path='doctors/my/availabilities')
    def get_login_doctor_availabilities(self, request):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get('current_user_id')

        service_url = f'http://web-visits:8600/doctor-availabilities/doctor/{user_id}/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        if response.status_code == status.HTTP_200_OK:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(data, status=response.status_code)

    def retrieve(self, request, pk=None):
        token = get_token(request)

        verify_token(token)

        service_url = f'http://web-visits:8600/doctor-availabilities/{pk}/'
        response = forward_request_to_service(service_url, token=token, method='get')

        data = response.json()

        if response.status_code == status.HTTP_200_OK:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(data, status=response.status_code)

    def create(self, request, *args, **kwargs):
        token = get_token(request)

        token_data = verify_token(token)

        current_user_role = token_data.get('current_user_role')
        user_id = token_data.get('current_user_id')

        service_url = 'http://web-visits:8600/doctor-availabilities/'
        response = forward_request_to_service(service_url, request.data, token, role=current_user_role, method='post')

        if user_id == request.data.get('doctor_id'):
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
        user_id = token_data.get('current_user_id')

        service_url = f'http://web-visits:8600/doctor-availabilities/{pk}/'
        response = forward_request_to_service(service_url, data=request.data, token=token, method='patch')

        if user_id == request.data.get('doctor_id'):
            if response.status_code == status.HTTP_200_OK:
                return Response({'message': 'Doctor availabilities updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(response.json(), status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_403_FORBIDDEN)

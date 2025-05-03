from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.support_functions import verify_token, forward_request_to_service, get_token

from core.settings import MEDICAL_RECORDS_SERVICE_URL, ACCOUNTS_SERVICE_URL, TOKEN_URL


class MedicalRecordsGatewayViewSet(GenericViewSet):
    @action(methods=['GET'], detail=False, url_path='patients/(?P<patient_id>\d+)/records')
    def get_records(self, request, patient_id=None):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get(f'{TOKEN_URL}/user_id')
        role = token_data.get(f'{TOKEN_URL}/role')

        service_url = f'{MEDICAL_RECORDS_SERVICE_URL}/patients/{patient_id}/medical-records/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        if user_id == patient_id or role == 'Doctor':
            if response.status_code == status.HTTP_200_OK:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(data, status=response.status_code)
        else:
            return Response({'detail': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get(f'{TOKEN_URL}/user_id')
        role = token_data.get(f'{TOKEN_URL}/role')

        service_url = f'{MEDICAL_RECORDS_SERVICE_URL}/{pk}/'
        response = forward_request_to_service(service_url, token=token, method='get')

        data = response.json()

        if user_id == data.get('patient_id') or role == 'Doctor':
            if response.status_code == status.HTTP_200_OK:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(data, status=response.status_code)
        return Response({'detail': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['PATCH'], detail=True, url_path='update')
    def update_medical_records(self, request, pk=None):
        token = get_token(request)
        token_data = verify_token(token)
        user_id = token_data.get(f'{TOKEN_URL}/user_id')

        accounts_url = f"{ACCOUNTS_SERVICE_URL}/users/{request.data.get('doctor_id')}/"
        response = forward_request_to_service(url=accounts_url, method='get')

        service_url = f'{MEDICAL_RECORDS_SERVICE_URL}/{pk}/'

        if user_id == response.json().get('auth0_id'):
            response = forward_request_to_service(service_url, data=request.data, token=token, method='patch')
            if response.status_code == status.HTTP_200_OK:
                return Response({'message': 'Medical records updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(status=response.status_code)
        else:
            return Response({'message': 'Unauthorized access.'}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request):
        token = get_token(request)

        token_data = verify_token(token)

        current_user_role = token_data.get(f'{TOKEN_URL}/role')
        response = forward_request_to_service(MEDICAL_RECORDS_SERVICE_URL, request.data, token, role=current_user_role,
                                                    method='post')

        if response.status_code == status.HTTP_201_CREATED:
            return Response(response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)

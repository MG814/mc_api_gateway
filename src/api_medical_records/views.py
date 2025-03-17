from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.support_functions import verify_token, forward_request_to_service, get_token


class MedicalRecordsGatewayViewSet(GenericViewSet):
    @action(methods=['GET'], detail=False, url_path='patients/(?P<patient_id>\d+)/records')
    def get_records(self, request, patient_id=None):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get('https://user-info/user_id')
        role = token_data.get('https://user-info/role')

        service_url = f'http://web-medical-records:8300/patients/{patient_id}/medical-records/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        if user_id == patient_id or role == 'Doctor': # DOCTOR
            if response.status_code == status.HTTP_200_OK:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(data, status=response.status_code)
        else:
            return Response({'detail': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

    def retrieve(self, request, pk=None):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get('https://user-info/user_id')
        role = token_data.get('https://user-info/role')

        service_url = f'http://web-medical-records:8300/{pk}/'
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
        user_id = token_data.get('https://user-info/user_id')

        service_url = f'http://web-medical-records:8300/{pk}/'

        if user_id == request.data.get('doctor_id'):
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

        current_user_role = token_data.get('https://user-info/role')
        service_url = 'http://web-medical-records:8300/'
        response = forward_request_to_service(service_url, request.data, token, role=current_user_role,
                                                    method='post')

        if response.status_code == status.HTTP_201_CREATED:
            return Response(response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response(response.json(), status=response.status_code)

from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from utils.support_functions import verify_token, forward_request_to_service, get_token


class MedicalRecordsGatewayViewSet(GenericViewSet):
    @action(methods=['GET'], detail=False, url_path='patients/my/records')
    def get_login_user_records(self, request):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get('current_user_id')

        service_url = f'http://web-medical-records:8300/patients/{user_id}/medical-records/'
        response = forward_request_to_service(service_url, token=token, method='get')
        data = response.json()

        if response.status_code == status.HTTP_200_OK:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(data, status=response.status_code)
# Update
    @action(methods=['GET'], detail=False, url_path='patients/(?P<patient_id>\d+)/records')
    def get_records(self, request, patient_id=None):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get('current_user_id')
        role = token_data.get('current_user_role')

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
# Update
    def retrieve(self, request, pk=None):
        token = get_token(request)

        token_data = verify_token(token)
        user_id = token_data.get('current_user_id')
        role = token_data.get('current_user_role')

        service_url = f'http://web-medical-records:8300/{pk}/'
        response = forward_request_to_service(service_url, token=token, method='get')

        data = response.json()

        if user_id == data.get('patient_id') or role == 'Doctor':
            if response.status_code == status.HTTP_200_OK:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(data, status=response.status_code)
        return Response({'detail': 'Unauthorized access.'}, status=status.HTTP_401_UNAUTHORIZED)

# Update
    def create(self, request):
        token = get_token(request)

        token_data = verify_token(token)

        current_user_role = token_data.get('current_user_role')
        visits_service_url = 'http://web-medical-records:8300/'
        visit_response = forward_request_to_service(visits_service_url, request.data, token, role=current_user_role,
                                                    method='post')

        if visit_response.status_code == status.HTTP_201_CREATED:
            return Response(visit_response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response(visit_response.json(), status=visit_response.status_code)

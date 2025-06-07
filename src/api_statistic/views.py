import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class StatisticGatewayView(APIView):

    def post(self, request):
        try:
            response = requests.post(
                "http://web-statistic:8200/graphql/",
                json=request.data,
                timeout=10
            )
            return Response(response.json(), status=response.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

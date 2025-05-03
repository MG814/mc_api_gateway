from django.urls import path
from .views import StatisticGatewayView

urlpatterns = [
    path("statistic/", StatisticGatewayView.as_view(), name="statistic"),
]

from django.urls import path
from .views import LoginGatewayView, RegisterGatewayView, UserAddressGatewayView

urlpatterns = [
    path('login/', LoginGatewayView.as_view(), name='login-gateway'),
    path('register/', RegisterGatewayView.as_view(), name='register-gateway'),
    path('user/address/', UserAddressGatewayView.as_view(), name='user-address-gateway'),
]

from django.urls import path
from rest_framework import routers
from .views import LoginGatewayView, RegisterGatewayView, UserAddressGatewayView, LogoutView, UpdateUserGatewayView

router = routers.SimpleRouter()
router.register('patients/addresses', UserAddressGatewayView, basename='address')
router.register('update', UpdateUserGatewayView, basename='update-user')

urlpatterns = [
    path("login/", LoginGatewayView.as_view(), name="auth0-login"),
    path("register/", RegisterGatewayView.as_view(), name="auth0-register"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
urlpatterns += router.urls

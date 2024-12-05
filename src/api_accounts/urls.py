from rest_framework import routers
from .views import LoginGatewayView, RegisterGatewayView, UserAddressGatewayView

router = routers.SimpleRouter()
router.register('patients/addresses', UserAddressGatewayView, basename='address')
router.register('login', LoginGatewayView, basename='login')
router.register('register', RegisterGatewayView, basename='register')

urlpatterns = router.urls

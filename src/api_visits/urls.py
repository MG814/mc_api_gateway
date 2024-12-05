from rest_framework import routers

from .views import VisitGatewayViewSet, DoctorAvailabilityGatewayViewSet

router = routers.SimpleRouter()
router.register('visits', VisitGatewayViewSet, basename='visit')
router.register('doctor-availabilities', DoctorAvailabilityGatewayViewSet, basename='availability')


urlpatterns = [
]
urlpatterns += router.urls

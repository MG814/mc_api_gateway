from .views import MedicalRecordsGatewayViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('medical-records', MedicalRecordsGatewayViewSet, basename='medical-records')

urlpatterns = router.urls

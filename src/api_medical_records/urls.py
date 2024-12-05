from django.urls import path
from .views import MedicalRecordsGatewayViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('', MedicalRecordsGatewayViewSet, basename='create-visit')

urlpatterns = [
]
urlpatterns += router.urls
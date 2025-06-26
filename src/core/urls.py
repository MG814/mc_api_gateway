from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api_accounts.urls')),
    path('api/', include('api_visits.urls')),
    path('api/', include('api_medical_records.urls')),
    path('api/', include('api_token_jwt.urls')),
    path('api/', include('api_statistic.urls')),
]
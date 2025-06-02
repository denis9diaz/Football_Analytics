from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', lambda request: redirect('admin/')),
    path('admin/', admin.site.urls),
    path('api/', include('analisis.urls')),
    path('api/auth/', include('customauth.urls')),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

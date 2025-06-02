from django.urls import path
from .views import RegisterView, ActivateUserView, ValidateTokenView, SendTempPasswordView, ForceChangePasswordView
from .custom_token import CustomTokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/', ActivateUserView.as_view(), name='activate'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('validate-token/', ValidateTokenView.as_view(), name='validate-token'),
    path("send_temp_password/", SendTempPasswordView.as_view()),
    path('force_change_password/', ForceChangePasswordView.as_view(), name='force_change_password'),
]

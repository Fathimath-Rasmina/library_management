# urls.py
from django.urls import path

from ..views.user_views import RegistrationAPIView, LoginAPIView, MyTokenObtainPairView

# * JWT
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    #####
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
]

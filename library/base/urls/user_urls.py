# urls.py
from django.urls import path

from ..views.user_views import (
    RegistrationAPIView,
    LoginAPIView,
    MyTokenObtainPairView,
    MemberListCreateView,
    MemberRetrieveUpdateDeleteView,
    UserProfileView,
)

# * JWT
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("user_profile/<int:user_id>/", UserProfileView.as_view(), name="user_profile"),
    path("manage_members/", MemberListCreateView.as_view(), name="manage_member"),
    #
    #
    path(
        "manage_members/<int:pk>/",
        MemberRetrieveUpdateDeleteView.as_view(),
        name="member_crud",
    ),
]

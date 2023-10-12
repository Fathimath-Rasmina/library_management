# views.py
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from ..serializers import UserSerializer, LoginSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from ..models import MyUser
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsLibrarianOrReadOnly
from rest_framework import generics


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            user = authenticate(username=username, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                )

        return Response(
            {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


# * user profile
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = MyUser.objects.get(pk=user_id)
        if user == request.user:
            data = user
            serializer = UserSerializer(data)
            return Response(serializer.data)
        else:
            return Response(
                {"message": "Unauthorized"}, status=status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, user_id):
        user = MyUser.objects.get(pk=user_id)
        if user == request.user:
            data = request.data
            serializer = UserSerializer(user, data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if "password" in data:
                    user.set_password(data["password"])
                    user.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Unauthorized"}, status=status.HTTP_400_BAD_REQUEST
            )


# view for member creation and view member list
class MemberListCreateView(generics.ListCreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]


# view for member CRUD operations
class MemberRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]

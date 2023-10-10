# serializers.py
from rest_framework import serializers
from .models import MyUser, Books, BookRequests
from django.core.validators import EmailValidator
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = "__all__"

        extra_kwargs = {
            "password": {"write_only": True}  # *password should be write only
        }

    email = serializers.EmailField(
        validators=[
            EmailValidator(message="Please enter a valid email address."),
            UniqueValidator(queryset=MyUser.objects.all()),
        ]
    )

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be minimum 8 characters")
        return value

    def create(self, validated_data):
        user = MyUser.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
        )

        password = validated_data["password"]
        user.set_password(password)
        print(user.password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = "__all__"


class BookRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRequests
        fields = "__all__"


# class RentedBookSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = RentedBook
#         fields = "__all__"

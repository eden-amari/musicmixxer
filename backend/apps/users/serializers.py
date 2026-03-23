from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.serializers import JWTSerializer
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return email

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already taken.")
        return username

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email"),
            "password1": self.validated_data.get("password1"),
            "username": self.validated_data.get("username"),
        }

    def save(self, request):
        user = super().save(request)

        user.username = self.validated_data.get("username")
        user.save()

        return user


class CustomJWTSerializer(JWTSerializer):

    def to_representation(self, instance):
        user = instance["user"]  # ✅ FIX HERE

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "pk": user.pk,
                "username": user.username,
                "email": user.email,
            },
        }
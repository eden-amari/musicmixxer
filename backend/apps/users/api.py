from ninja import Router, Schema
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from google.oauth2 import id_token
from google.auth.transport import requests

import os

from .auth import JWTAuth
from .schemas import UserOut, UpdateUserSchema
from .services import update_user

router = Router(auth=JWTAuth())
User = get_user_model()


# ✅ GET CURRENT USER
@router.get("/me", response=UserOut)
def get_me(request):
    user = request.auth

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "name": user.name,
        "bio": user.bio,
    }


# ✅ UPDATE USER PROFILE
@router.patch("/me", response=UserOut)
def update_me(request, data: UpdateUserSchema):
    user = request.auth
    user = update_user(user, data)

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "name": user.name,
        "bio": user.bio,
    }


# ✅ LOGOUT
class LogoutSchema(Schema):
    refresh: str


@router.post("/logout")
def logout(request, data: LogoutSchema):
    try:
        token = RefreshToken(data.refresh)
        token.blacklist()

        return {
            "success": True,
            "message": "Logged out successfully"
        }

    except Exception:
        return {
            "success": False,
            "message": "Invalid or expired token"
        }


# =========================
# 🔥 GOOGLE AUTH
# =========================

class GoogleAuthSchema(Schema):
    token: str


@router.post("/auth/google", auth=None)
def google_login(request, data: GoogleAuthSchema):
    try:
        idinfo = id_token.verify_oauth2_token(
            data.token,
            requests.Request(),
            os.getenv("GOOGLE_CLIENT_ID")
        )

        email = idinfo.get("email")
        name = idinfo.get("name", "")

        if not email:
            return {"error": "Email not available"}

        # 🔥 username generation
        base_username = email.split("@")[0]
        username = base_username

        if User.objects.filter(username=username).exists():
            username = f"{base_username}_{User.objects.count()}"

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "name": name,
            }
        )

        if not created and not user.name:
            user.name = name
            user.save()

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "name": user.name,
                "bio": user.bio,
            }
        }

    except Exception as e:
        return {
            "error": "Invalid Google token",
            "details": str(e)
        }
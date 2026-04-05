from ninja import Router, Schema
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import logging

from .auth import JWTAuth
from .schemas import UpdateUserSchema
from .services import update_user

logger = logging.getLogger(__name__)
User = get_user_model()

# Create router WITHOUT auth (we'll apply it per-endpoint)
router = Router()


# =========================
# HELPERS
# =========================

def success(data=None):
    return {
        "success": True,
        "data": data,
        "error": None
    }


def failure(e):
    return {
        "success": False,
        "data": None,
        "error": {
            "message": str(e),
            "type": e.__class__.__name__
        }
    }


# =========================
# GET CURRENT USER
# =========================

@router.get("/me", auth=JWTAuth())  # Apply auth here
def get_me(request):
    try:
        user = request.auth  # Use request.auth instead of request.user
        logger.info(f"📝 /me endpoint - User: {user}")

        return success({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "name": user.name,
            "bio": user.bio,
        })

    except Exception as e:
        logger.error(f"❌ /me error: {str(e)}")
        return failure(e)


# =========================
# UPDATE USER PROFILE
# =========================

@router.patch("/me", auth=JWTAuth())  # Apply auth here
def update_me(request, data: UpdateUserSchema):
    try:
        user = request.auth  # Use request.auth instead of request.user
        user = update_user(user, data)

        return success({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "name": user.name,
            "bio": user.bio,
        })

    except Exception as e:
        return failure(e)


# =========================
# LOGOUT
# =========================

class LogoutSchema(Schema):
    refresh: str


@router.post("/logout", auth=JWTAuth())  # Apply auth here
def logout(request, data: LogoutSchema):
    try:
        token = RefreshToken(data.refresh)
        token.blacklist()

        return success()

    except Exception as e:
        return failure(e)


# =========================
# GOOGLE AUTH (PUBLIC)
# =========================

class GoogleAuthSchema(Schema):
    token: str


@router.post("/google", auth=None)
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
            raise Exception("Email not available")

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

        return success({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "name": user.name,
                "bio": user.bio,
            }
        })

    except Exception as e:
        return failure(e)


# =========================
# TEST TOKEN (TEMPORARY)
# =========================

@router.post("/test-token", auth=None)
def create_test_token(request):
    """TEMPORARY - For testing only. Remove in production."""
    try:
        user, created = User.objects.get_or_create(
            email="test@example.com",
            defaults={
                "username": "testuser",
                "name": "Test User"
            }
        )
        
        logger.info(f"{'Created' if created else 'Found'} test user: {user.email}")
        
        refresh = RefreshToken.for_user(user)
        
        return success({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "name": user.name,
            }
        })
    except Exception as e:
        logger.error(f"Test token error: {str(e)}")
        return failure(e)
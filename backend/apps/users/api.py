from ninja import Router, Schema
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from django.core.exceptions import ObjectDoesNotExist
import os
import logging
from django.contrib.auth import authenticate
from datetime import timedelta
from rest_framework_simplejwt.exceptions import TokenError

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


def infer_status_code(e):
    if isinstance(e, PermissionError):
        return 403
    if isinstance(e, ObjectDoesNotExist):
        return 404
    if isinstance(e, (ValueError, TokenError)):
        message = str(e).lower()
        if "not found" in message:
            return 404
        if "access denied" in message or "permission" in message:
            return 403
        return 400
    return 500


def failure(e, status_code=None):
    return JsonResponse({
        "success": False,
        "data": None,
        "error": {
            "message": str(e),
            "type": e.__class__.__name__
        }
    }, status=status_code or infer_status_code(e))


# =========================
# GET CURRENT USER
# =========================

@router.get("/me", auth=JWTAuth())
def get_me(request):
    try:
        user = request.auth
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

@router.patch("/me", auth=JWTAuth())
def update_me(request, data: UpdateUserSchema):
    try:
        user = request.auth
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


@router.post("/logout", auth=JWTAuth())
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
# LOGIN WITH REMEMBER ME
# =========================

class LoginSchema(Schema):
    email: str
    password: str
    remember_me: bool = False


@router.post("/login/remember-me", auth=None)
def login_remember_me(request, data: LoginSchema):
    try:
        try:
            account = User.objects.get(email__iexact=data.email)
        except ObjectDoesNotExist:
            return failure(ValueError("Invalid credentials"), status_code=401)

        user = authenticate(username=account.username, password=data.password)

        if not user:
            return failure(ValueError("Invalid credentials"), status_code=401)

        refresh = RefreshToken.for_user(user)

        # If remember_me is True, extend the refresh token lifetime
        if data.remember_me:
            refresh.set_exp(lifetime=timedelta(days=30))  # 30 days instead of 7

        return success({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'name': user.name,
            }
        })

    except Exception as e:
        return failure(e)

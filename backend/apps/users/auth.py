from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework.exceptions import AuthenticationFailed


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            UntypedToken(token)
            jwt_auth = JWTAuthentication()
            user, _ = jwt_auth.authenticate(request)

            return user

        except Exception:
            raise AuthenticationFailed("Invalid or expired token")
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from ninja.errors import HttpError
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        # This log should appear if the method is being called
        logger.info("=" * 50)
        logger.info(f"🔐 JWTAuth.authenticate() called")
        logger.info(f"Token received: {token[:30] if token else 'None'}...")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info("=" * 50)
        
        if not token:
            logger.error("❌ No token provided")
            return None
        
        try:
            # Validate and decode token using SimpleJWT
            access_token = AccessToken(token)
            user_id = access_token.get("user_id")
            
            logger.info(f"✅ Token valid - user_id: {user_id}")
            
            if not user_id:
                logger.error("❌ No user_id in token")
                return None

            user = User.objects.get(id=user_id)
            logger.info(f"✅ User found: {user.email}")
            return user

        except InvalidToken as e:
            logger.error(f"❌ InvalidToken: {str(e)}")
            return None
        except TokenError as e:
            logger.error(f"❌ TokenError: {str(e)}")
            return None
        except User.DoesNotExist:
            logger.error(f"❌ User not found for id: {user_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
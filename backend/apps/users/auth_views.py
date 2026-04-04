from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.response import Response

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # ✅ return the NEW rotated refresh token, not the old one
        if response.status_code == 200 and "refresh" not in response.data:
            response.data["refresh"] = request.data.get("refresh")
        return response
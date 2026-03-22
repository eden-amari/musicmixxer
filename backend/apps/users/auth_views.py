from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.response import Response


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # ensure refresh is returned if rotation enabled
        if "refresh" not in response.data:
            refresh = request.data.get("refresh")
            response.data["refresh"] = refresh

        return response
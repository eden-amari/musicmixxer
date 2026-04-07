from django.urls import path, include
from ninja import NinjaAPI
from apps.users.auth_views import CustomTokenRefreshView
from apps.users.api import router as users_router
from apps.playlists.api.routes import router as playlist_router
from apps.integrations.spotify.api.routes import router as spotify_router
from apps.imports.api.routes import router as imports_router

api = NinjaAPI()
api.add_router("/users/", users_router)
api.add_router("/playlists/", playlist_router)
api.add_router("/auth/spotify/", spotify_router)
api.add_router("/imports/", imports_router)

urlpatterns = [
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/", api.urls),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
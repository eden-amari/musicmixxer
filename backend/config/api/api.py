from ninja import NinjaAPI
from apps.users.api.views import router as users_router

api = NinjaAPI(title="MusicMixxer API")

api.add_router("/users/", users_router)
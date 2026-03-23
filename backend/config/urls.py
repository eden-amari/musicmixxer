"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from ninja import NinjaAPI
from apps.users.auth_views import CustomTokenRefreshView
from apps.users.api import router as users_router

api = NinjaAPI()
api.add_router("/users/", users_router)



urlpatterns = [
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/", api.urls),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),

    # ✅ USE CUSTOM VIEW
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
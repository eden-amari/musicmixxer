from ninja import Router
from django.shortcuts import redirect
from urllib.parse import urlencode
from django.conf import settings
import requests

router = Router()


@router.get("/login")
def spotify_login(request):
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": " ".join([
            "user-read-private",
            "user-read-email",
            "playlist-read-private",
            "playlist-read-collaborative",
            "playlist-modify-private",
            "playlist-modify-public",
        ]),
        "show_dialog": True,
    }

    url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return redirect(url)

@router.get("/callback")
def spotify_callback(request, code: str = None, error: str = None):

    if error:
        return {"error": error}

    if not code:
        return {"error": "Missing code"}

    token_url = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=data)

    if response.status_code != 200:
        return {"error": response.text}

    token_data = response.json()

    # ⚠️ TEMP: return token (later store in DB)
    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token")
    }
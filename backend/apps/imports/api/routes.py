from ninja import Router, File
from ninja.files import UploadedFile

from apps.users.auth import JWTAuth
from apps.imports.domain.services import ImportService

router = Router()  # ❌ REMOVE global auth


# =========================
# HELPERS
# =========================

def get_spotify_token(request, required=False):
    token = request.headers.get("X-Spotify-Access-Token")
    if required and not token:
        raise Exception("Spotify token required")
    return token


def success(data=None):
    return {"success": True, "data": data, "error": None}


def failure(e):
    return {
        "success": False,
        "data": None,
        "error": {
            "message": str(e),
            "type": e.__class__.__name__,
        },
    }


# =========================
# IMPORT CSV
# =========================

@router.post("/csv", auth=JWTAuth())  # ✅ apply per-route auth
def import_csv(request, file: UploadedFile = File(...), playlist_id: int = None):
    try:
        user = request.auth  # ✅ FIX: use request.auth

        spotify_token = get_spotify_token(request)

        result = ImportService.import_file(
            file=file.file,
            file_type="csv",
            access_token=spotify_token,
            user=user,
            playlist_id=playlist_id,
        )

        return success(result)

    except Exception as e:
        return failure(e)


# =========================
# IMPORT JSON
# =========================

@router.post("/json", auth=JWTAuth())  # ✅ apply per-route auth
def import_json(request, file: UploadedFile = File(...), playlist_id: int = None):
    try:
        user = request.auth  # ✅ FIX

        spotify_token = get_spotify_token(request)

        result = ImportService.import_file(
            file=file.file,
            file_type="json",
            access_token=spotify_token,
            user=user,
            playlist_id=playlist_id,
        )

        return success(result)

    except Exception as e:
        return failure(e)
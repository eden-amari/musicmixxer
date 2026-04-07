# apps/imports/api/routes.py

from ninja import Router, File
from ninja.files import UploadedFile

from apps.users.auth import JWTAuth
from apps.imports.domain.services import ImportService

router = Router(auth=JWTAuth())


# =========================================================
# HELPERS
# =========================================================

def _extract_spotify_token(request):
    """
    Extract Spotify token from custom header.

    Expected:
        X-Spotify-Token: <token>
    """
    return request.headers.get("X-Spotify-Token")


# =========================================================
# CSV IMPORT
# =========================================================

@router.post("/csv")
def import_csv(
    request,
    file: UploadedFile = File(...),
    playlist_id: int = None,
):
    spotify_token = _extract_spotify_token(request)

    try:
        result = ImportService.import_file(
            file=file.file,
            file_type="csv",
            access_token=spotify_token,   # 🔥 optional
            user=request.user,
            playlist_id=playlist_id
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# =========================================================
# JSON IMPORT
# =========================================================

@router.post("/json")
def import_json(
    request,
    file: UploadedFile = File(...),
    playlist_id: int = None,
):
    spotify_token = _extract_spotify_token(request)

    try:
        result = ImportService.import_file(
            file=file.file,
            file_type="json",
            access_token=spotify_token,   # 🔥 optional
            user=request.user,
            playlist_id=playlist_id
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
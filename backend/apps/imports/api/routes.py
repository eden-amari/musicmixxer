# apps/imports/api/routes.py

from ninja import Router, File
from ninja.files import UploadedFile

from apps.imports.domain.services import ImportService

router = Router()


def _extract_token(request):
    """
    Extract Spotify access token from Authorization header.

    Expected:
        Authorization: Bearer <token>
    """
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    return auth_header.replace("Bearer ", "").strip()


@router.post("/csv")
def import_csv(request, file: UploadedFile = File(...)):
    access_token = _extract_token(request)

    if not access_token:
        return {
            "success": False,
            "error": "Spotify access token required"
        }

    return ImportService.import_file(
        file=file.file,
        file_type="csv",
        access_token=access_token
    )


@router.post("/json")
def import_json(request, file: UploadedFile = File(...)):
    access_token = _extract_token(request)

    if not access_token:
        return {
            "success": False,
            "error": "Spotify access token required"
        }

    return ImportService.import_file(
        file=file.file,
        file_type="json",
        access_token=access_token
    )
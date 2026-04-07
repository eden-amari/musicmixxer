from ninja import Router, Schema
from django.http import HttpRequest
from typing import Optional, List

from apps.users.auth import JWTAuth
from apps.playlists.services.playlist_service import PlaylistService
from apps.playlists.services.playlist_item_service import PlaylistItemService

from apps.playlists.domain.spotify_import_service import SpotifyImportService
from apps.playlists.domain.spotify_export_service import SpotifyExportService
from apps.playlists.domain.organization_service import OrganizationService

router = Router(auth=JWTAuth(), tags=["playlists"])


# =========================
# HELPERS
# =========================

def _extract_spotify_token(request):
    """
    Extract Spotify token from custom header.
    Expected:
        X-Spotify-Token: <token>
    """
    return request.headers.get("X-Spotify-Token")


# =========================
# SCHEMAS
# =========================

class CreatePlaylistSchema(Schema):
    title: str
    description: str = ""


class ImportSpotifySchema(Schema):
    playlist_id: str


class ExportSpotifySchema(Schema):
    name: Optional[str] = None


class OrganizeSchema(Schema):
    mode: str


# =========================
# CRUD
# =========================

@router.post("/")
def create_playlist(request: HttpRequest, payload: CreatePlaylistSchema):
    playlist = PlaylistService.create_playlist(
        user=request.user,
        title=payload.title,
        description=payload.description
    )

    return {
        "success": True,
        "data": {
            "id": playlist.id,
            "title": playlist.title
        }
    }


@router.get("/")
def get_playlists(request: HttpRequest):
    playlists = PlaylistService.get_user_playlists(request.user)

    return {
        "success": True,
        "data": [
            {
                "id": p.id,
                "title": p.title,
                "is_public": p.is_public
            }
            for p in playlists
        ]
    }


@router.get("/{playlist_id}")
def get_playlist(request: HttpRequest, playlist_id: int):
    playlist = PlaylistService.get_playlist_with_items(
        playlist_id,
        user=request.user
    )

    return {
        "success": True,
        "data": playlist
    }


@router.patch("/{playlist_id}")
def update_playlist(request: HttpRequest, playlist_id: int, data: dict):
    playlist = PlaylistService.update_playlist(
        playlist_id,
        request.user,
        data
    )

    return {
        "success": True,
        "data": {
            "id": playlist.id,
            "title": playlist.title
        }
    }


@router.delete("/{playlist_id}")
def delete_playlist(request: HttpRequest, playlist_id: int):
    PlaylistService.delete_playlist(playlist_id, request.user)

    return {"success": True}


# =========================
# ITEMS
# =========================

@router.post("/{playlist_id}/items")
def add_song(
    request: HttpRequest,
    playlist_id: int,
    track_id: int,
    position: Optional[int] = None
):
    # 🔥 Ownership check
    PlaylistService.get_playlist(playlist_id, user=request.user)

    item = PlaylistItemService.add_song_to_playlist(
        playlist_id,
        track_id,
        position
    )

    return {
        "success": True,
        "data": {
            "id": item.id,
            "track_id": item.track_id,
            "position": item.position
        }
    }


@router.delete("/{playlist_id}/items/{position}")
def remove_song(request: HttpRequest, playlist_id: int, position: int):
    PlaylistService.get_playlist(playlist_id, user=request.user)

    PlaylistItemService.remove_song_from_playlist(playlist_id, position)

    return {"success": True}


@router.post("/{playlist_id}/reorder")
def reorder_playlist(
    request: HttpRequest,
    playlist_id: int,
    new_order: List[int]
):
    PlaylistService.get_playlist(playlist_id, user=request.user)

    PlaylistItemService.reorder_playlist(playlist_id, new_order)

    return {"success": True}


# =========================
# 🔥 SPOTIFY IMPORT
# =========================

@router.post("/spotify/import")
def import_spotify(request: HttpRequest, payload: ImportSpotifySchema):

    spotify_token = _extract_spotify_token(request)

    if not spotify_token:
        return {
            "success": False,
            "error": "Spotify token required"
        }

    result = SpotifyImportService.import_playlist(
        user=request.user,
        playlist_id=payload.playlist_id,
        access_token=spotify_token
    )

    return {
        "success": True,
        "data": result
    }


# =========================
# 🔥 ORGANIZE
# =========================

@router.post("/{playlist_id}/organize")
def organize_playlist(
    request: HttpRequest,
    playlist_id: int,
    payload: OrganizeSchema
):
    playlist = PlaylistService.get_playlist_with_items(
        playlist_id,
        user=request.user
    )

    items = playlist.get("items", [])

    tracks = [
        {
            "id": item["track"]["id"],
            "title": item["track"]["title"],
            "bpm": item["track"]["bpm"],
            "energy": item["track"]["energy"],
            "valence": item["track"]["valence"],
        }
        for item in items if item.get("track")
    ]

    ordered_tracks = OrganizationService.organize(
        tracks,
        strategy=payload.mode
    )

    return {
        "success": True,
        "data": ordered_tracks
    }


# =========================
# 🔥 EXPORT
# =========================

@router.post("/{playlist_id}/export")
def export_playlist(
    request: HttpRequest,
    playlist_id: int,
    payload: ExportSpotifySchema
):
    spotify_token = _extract_spotify_token(request)

    if not spotify_token:
        return {
            "success": False,
            "error": "Spotify token required"
        }

    PlaylistService.get_playlist(playlist_id, user=request.user)

    result = SpotifyExportService.export(
        playlist_id=playlist_id,
        access_token=spotify_token,
        name=payload.name
    )

    return {
        "success": True,
        "data": result
    }
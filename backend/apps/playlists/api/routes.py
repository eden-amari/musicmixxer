from ninja import Router, Schema
from django.http import HttpRequest
from typing import Optional, List

from apps.users.auth import JWTAuth
from apps.playlists.services.playlist_service import PlaylistService
from apps.playlists.services.playlist_item_service import PlaylistItemService

from apps.playlists.domain.spotify_import_service import SpotifyImportService
from apps.playlists.domain.spotify_export_service import SpotifyExportService
from apps.playlists.domain.organization_service import OrganizationService
from apps.integrations.spotify.client import SpotifyClient

router = Router(tags=["playlists"])


# =========================
# HELPERS
# =========================

def get_spotify_token(request, required=False):
    token = request.headers.get("X-Spotify-Access-Token")
    if required and not token:
        raise ValueError("Spotify token required")
    return token


def success(data=None):
    return {"success": True, "data": data, "error": None}


def failure(e):
    return {
        "success": False,
        "data": None,
        "error": {
            "message": str(e),
            "type": e.__class__.__name__
        }
    }


# =========================
# SCHEMAS
# =========================

class CreatePlaylistSchema(Schema):
    title: str
    description: str = ""


class UpdatePlaylistSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class AddSongSchema(Schema):
    track_id: int
    position: Optional[int] = None


class ReorderSchema(Schema):
    new_order: List[int]


class ImportSpotifySchema(Schema):
    playlist_id: str


class ExportSpotifySchema(Schema):
    name: Optional[str] = None


class OrganizeSchema(Schema):
    mode: str


# =========================
# CRUD
# =========================

@router.post("/", auth=JWTAuth())
def create_playlist(request: HttpRequest, payload: CreatePlaylistSchema):
    try:
        user = request.auth

        playlist = PlaylistService.create_playlist(
            user=user,
            title=payload.title,
            description=payload.description
        )

        return success({"id": playlist.id, "title": playlist.title})

    except Exception as e:
        return failure(e)


@router.get("/", auth=JWTAuth())
def get_playlists(request: HttpRequest):
    try:
        user = request.auth

        playlists = PlaylistService.get_user_playlists(user)

        return success([
            {"id": p.id, "title": p.title, "is_public": p.is_public}
            for p in playlists
        ])

    except Exception as e:
        return failure(e)


@router.get("/{playlist_id}", auth=JWTAuth())
def get_playlist(request: HttpRequest, playlist_id: int):
    try:
        user = request.auth

        playlist = PlaylistService.get_playlist_with_items(
            playlist_id,
            user=user
        )

        return success(playlist)

    except Exception as e:
        return failure(e)


@router.patch("/{playlist_id}", auth=JWTAuth())
def update_playlist(request: HttpRequest, playlist_id: int, payload: UpdatePlaylistSchema):
    try:
        user = request.auth

        playlist = PlaylistService.update_playlist(
            playlist_id,
            user,
            payload.dict(exclude_unset=True)
        )

        return success({"id": playlist.id, "title": playlist.title})

    except Exception as e:
        return failure(e)


@router.delete("/{playlist_id}", auth=JWTAuth())
def delete_playlist(request: HttpRequest, playlist_id: int):
    try:
        user = request.auth

        PlaylistService.delete_playlist(playlist_id, user)

        return success()

    except Exception as e:
        return failure(e)


# =========================
# ITEMS
# =========================

@router.post("/{playlist_id}/items", auth=JWTAuth())
def add_song(request: HttpRequest, playlist_id: int, payload: AddSongSchema):
    try:
        user = request.auth

        # Validate access
        PlaylistService.get_playlist(playlist_id, user=user)

        item = PlaylistItemService.add_song_to_playlist(
            playlist_id,
            payload.track_id,
            user,                 # ✅ FIXED
            payload.position
        )

        return success({
            "id": item.id,
            "track_id": item.track_id,
            "position": item.position
        })

    except Exception as e:
        return failure(e)


@router.delete("/{playlist_id}/items/{position}", auth=JWTAuth())
def remove_song(request: HttpRequest, playlist_id: int, position: int):
    try:
        user = request.auth

        PlaylistService.get_playlist(playlist_id, user=user)

        PlaylistItemService.remove_song_from_playlist(
            playlist_id,
            position,
            user                 # ✅ FIXED
        )

        return success()

    except Exception as e:
        return failure(e)


@router.post("/{playlist_id}/reorder", auth=JWTAuth())
def reorder_playlist(request: HttpRequest, playlist_id: int, payload: ReorderSchema):
    try:
        user = request.auth

        PlaylistService.get_playlist(playlist_id, user=user)

        PlaylistItemService.reorder_playlist(
            playlist_id,
            payload.new_order,
            user                 # ✅ FIXED
        )

        return success()

    except Exception as e:
        return failure(e)


# =========================
# SPOTIFY IMPORT
# =========================

@router.post("/spotify/import", auth=JWTAuth())
def import_spotify(request: HttpRequest, payload: ImportSpotifySchema):
    try:
        user = request.auth
        spotify_token = get_spotify_token(request, required=True)

        result = SpotifyImportService.import_playlist(
            user=user,
            playlist_id=payload.playlist_id,
            access_token=spotify_token
        )

        return success(result)

    except Exception as e:
        return failure(e)


# =========================
# ORGANIZE
# =========================

@router.post("/{playlist_id}/organize", auth=JWTAuth())
def organize_playlist(request: HttpRequest, playlist_id: int, payload: OrganizeSchema):
    try:
        user = request.auth

        playlist = PlaylistService.get_playlist_with_items(
            playlist_id,
            user=user
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

        return success(ordered_tracks)

    except Exception as e:
        return failure(e)


# =========================
# EXPORT
# =========================

@router.post("/{playlist_id}/export", auth=JWTAuth())
def export_playlist(request: HttpRequest, playlist_id: int, payload: ExportSpotifySchema):
    try:
        user = request.auth
        spotify_token = get_spotify_token(request, required=True)

        PlaylistService.get_playlist(playlist_id, user=user)

        result = SpotifyExportService.export(
            playlist_id=playlist_id,
            access_token=spotify_token,
            name=payload.name
        )

        return success(result)

    except Exception as e:
        return failure(e)

# =========================
# SPOTIFY READ
# =========================

@router.get("/spotify/playlists", auth=JWTAuth())
def get_spotify_playlists(request: HttpRequest):
    try:
        spotify_token = get_spotify_token(request, required=True)

        client = SpotifyClient(spotify_token)
        playlists = client.get_user_playlists()

        data = [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "tracks_count": p.get("tracks", {}).get("total", 0),  # 🔥 FIXED
                "image": p.get("images", [{}])[0].get("url") if p.get("images") else None,
            }
            for p in playlists
        ]

        return success(data)

    except Exception as e:
        return failure(e)


@router.get("/spotify/playlists/{playlist_id}", auth=JWTAuth())
def get_spotify_playlist_tracks(request: HttpRequest, playlist_id: str):
    try:
        spotify_token = get_spotify_token(request, required=True)

        client = SpotifyClient(spotify_token)
        items = client.get_playlist_items(playlist_id)

        data = []

        for item in items:
            track = item.get("item")   # ✅ FIXED

            if not track:
                continue

            data.append({
                "title": track.get("name"),
                "artist": track.get("artists", [{}])[0].get("name"),
                "spotify_id": track.get("id"),
                "album": track.get("album", {}).get("name"),
                "image": track.get("album", {}).get("images", [{}])[0].get("url"),
            })

        return success(data[:25])

    except Exception as e:
        return failure(e)
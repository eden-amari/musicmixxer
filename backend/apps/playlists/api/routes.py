from ninja import Router
from django.http import HttpRequest

from apps.playlists.services.playlist_service import PlaylistService
from apps.playlists.services.playlist_item_service import PlaylistItemService

router = Router()

@router.post("/")
def create_playlist(request: HttpRequest, title: str, description: str = ""):
    user = request.user

    playlist = PlaylistService.create_playlist(user, title, description)

    return {"id": playlist.id, "title": playlist.title}


@router.get("/")
def get_playlists(request: HttpRequest):
    user = request.user

    playlists = PlaylistService.get_user_playlists(user)

    return [
        {
            "id": p.id,
            "title": p.title,
            "is_public": p.is_public
        }
        for p in playlists
    ]

@router.get("/{playlist_id}")
def get_playlist(request: HttpRequest, playlist_id: int):
    user = request.user

    return PlaylistService.get_playlist_with_items(playlist_id, user=user)

@router.patch("/{playlist_id}")
def update_playlist(request: HttpRequest, playlist_id: int, data: dict):
    user = request.user

    playlist = PlaylistService.update_playlist(playlist_id, user, data)

    return {"id": playlist.id, "title": playlist.title}

@router.delete("/{playlist_id}")
def delete_playlist(request: HttpRequest, playlist_id: int):
    user = request.user

    PlaylistService.delete_playlist(playlist_id, user)

    return {"success": True}

@router.post("/{playlist_id}/items")
def add_song(request: HttpRequest, playlist_id: int, song_id: int, position: int = None):
    item = PlaylistItemService.add_song_to_playlist(
        playlist_id,
        song_id,
        position
    )

    return {
        "id": item.id,
        "song_id": item.song_id,
        "position": item.position
    }

@router.delete("/{playlist_id}/items/{position}")
def remove_song(request: HttpRequest, playlist_id: int, position: int):
    PlaylistItemService.remove_song_from_playlist(playlist_id, position)

    return {"success": True}


@router.post("/{playlist_id}/reorder")
def reorder_playlist(request: HttpRequest, playlist_id: int, new_order: list[int]):
    PlaylistItemService.reorder_playlist(playlist_id, new_order)

    return {"success": True}



from typing import Dict, List
from django.db import transaction

from apps.integrations.spotify.client import SpotifyClient
from apps.tracks.services.enrichment_service import EnrichmentService
from apps.tracks.services.track_services import TrackService
from apps.tracks.services.resolver import TrackResolver

from apps.playlists.services.playlist_service import PlaylistService
from apps.playlists.services.playlist_item_service import PlaylistItemService


class SpotifyImportService:
    """
    Domain-level Spotify import service.

    Responsibilities:
    - Fetch Spotify data
    - Normalize
    - Resolve
    - Enrich
    - Store
    - Attach to playlist
    """

    @staticmethod
    @transaction.atomic
    def import_playlist(user, playlist_id: str, access_token: str) -> Dict:

        client = SpotifyClient(access_token)

        playlist_data = client._request("GET", f"/playlists/{playlist_id}")

        playlist = PlaylistService.create_playlist(
            user=user,
            title=playlist_data.get("name"),
            description=playlist_data.get("description") or ""
        )

        items = client.get_playlist_items(playlist_id)

        stats = {
            "total": 0,
            "success": 0,
            "duplicates": 0,
            "failed": 0,
            "errors": []
        }

        for index, item in enumerate(items):
            stats["total"] += 1

            try:
                track = item.get("track")

                if not track or not track.get("id"):
                    stats["failed"] += 1
                    continue

                # --------------------
                # NORMALIZE
                # --------------------
                data = {
                    "title": track.get("name"),
                    "artist": track.get("artists")[0].get("name") if track.get("artists") else None,
                    "spotify_id": track.get("id"),
                    "genre": "unknown",
                }

                # --------------------
                # RESOLVE
                # --------------------
                try:
                    resolved = TrackResolver.resolve(data, access_token) or data
                except Exception:
                    resolved = data

                # --------------------
                # ENRICH
                # --------------------
                try:
                    enriched = EnrichmentService.enrich(resolved, access_token) or resolved
                except Exception:
                    enriched = resolved

                # --------------------
                # STORE
                # --------------------
                track_obj, created = TrackService.create_safe(enriched)

                if created:
                    stats["success"] += 1
                else:
                    stats["duplicates"] += 1

                # --------------------
                # ATTACH
                # --------------------
                PlaylistItemService.add_song_to_playlist(
                    playlist_id=playlist.id,
                    song_id=track_obj.id,
                    position=index
                )

            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append(str(e))

        return stats

    # 🔥 OPTIONAL: import all playlists
    @staticmethod
    def import_all_user_playlists(user, access_token: str) -> List[Dict]:

        client = SpotifyClient(access_token)
        playlists = client.get_user_playlists()

        results = []

        for p in playlists:
            try:
                result = SpotifyImportService.import_playlist(
                    user=user,
                    playlist_id=p["id"],
                    access_token=access_token
                )
                results.append({
                    "playlist": p["name"],
                    "stats": result
                })
            except Exception as e:
                results.append({
                    "playlist": p.get("name", "unknown"),
                    "error": str(e)
                })

        return results
from apps.playlists.models import Playlist, PlaylistItem


class PlaylistService:

    @staticmethod
    def create_playlist(user, title, description=""):
        if not title:
            raise ValueError("Title is required")

        return Playlist.objects.create(
            user=user,
            title=title,
            description=description
        )

    @staticmethod
    def get_playlist(playlist_id, user):
        try:
            return Playlist.objects.get(id=playlist_id, user=user)
        except Playlist.DoesNotExist:
            raise ValueError("Playlist not found")

    @staticmethod
    def get_user_playlists(user):
        return Playlist.objects.filter(user=user).order_by("-created_at")

    @staticmethod
    def update_playlist(playlist_id, user, data):
        playlist = PlaylistService.get_playlist(playlist_id, user)

        if "title" in data:
            if not data["title"]:
                raise ValueError("Title cannot be empty")
            playlist.title = data["title"]

        if "description" in data:
            playlist.description = data["description"]

        if "is_public" in data:
            playlist.is_public = data["is_public"]

        playlist.save()
        return playlist

    @staticmethod
    def delete_playlist(playlist_id, user):
        playlist = PlaylistService.get_playlist(playlist_id, user)
        playlist.delete()

    @staticmethod
    def get_playlist_with_items(playlist_id, user):
        playlist = PlaylistService.get_playlist(playlist_id, user)

        items = PlaylistItem.objects.filter(
            playlist=playlist
        ).select_related("track").order_by("position")

        return {
            "id": playlist.id,
            "title": playlist.title,
            "description": playlist.description,
            "is_public": playlist.is_public,
            "items": [
                {
                    "id": item.id,
                    "position": item.position,
                    "track": {
                        "id": item.track.id if item.track else None,
                        "title": item.track.title if item.track else None,
                        "bpm": item.track.bpm if item.track else None,
                        "energy": item.track.energy if item.track else None,
                        "valence": item.track.valence if item.track else None,
                    }
                }
                for item in items
            ]
        }

    @staticmethod
    def get_playlist_items_only(playlist_id, user):
        playlist = PlaylistService.get_playlist(playlist_id, user)

        return PlaylistItem.objects.filter(
            playlist=playlist
        ).order_by("position")
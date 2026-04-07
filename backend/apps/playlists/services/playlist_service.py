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
    def get_playlist(playlist_id):
        return Playlist.objects.get(id=playlist_id)

    @staticmethod
    def get_user_playlists(user):
        return Playlist.objects.filter(user=user)

    @staticmethod
    def update_playlist(playlist_id, user, data):
        playlist = Playlist.objects.get(id=playlist_id)

        if playlist.user != user:
            raise PermissionError("Not allowed")

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
        playlist = Playlist.objects.get(id=playlist_id)

        if playlist.user != user:
            raise PermissionError("Not allowed")

        playlist.delete()
    
    @staticmethod
    def get_playlist_with_items(playlist_id, user=None):
        playlist = Playlist.objects.get(id=playlist_id)

        # Optional: enforce access control
        if not playlist.is_public:
            if user is None or playlist.user != user:
                raise PermissionError("Not allowed")

        # Fetch ordered items
        items = PlaylistItem.objects.filter(
            playlist=playlist
        ).order_by('position')

        return {
            "id": playlist.id,
            "title": playlist.title,
            "description": playlist.description,
            "is_public": playlist.is_public,
            "items": [
                {
                    "id": item.id,
                    "song_id": item.song_id,
                    "position": item.position
                }
                for item in items
            ]
        }

    @staticmethod
    def get_playlist_items_only(playlist_id):
        return PlaylistItem.objects.filter(
            playlist_id=playlist_id
        ).order_by('position')
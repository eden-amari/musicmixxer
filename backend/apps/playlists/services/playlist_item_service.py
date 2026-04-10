from django.db import transaction, models

from apps.playlists.models import Playlist, PlaylistItem
from apps.tracks.models import Track


class PlaylistItemService:

    @staticmethod
    @transaction.atomic
    def add_song_to_playlist(playlist_id, track_id, user, position=None):
        # 🔐 Validate playlist ownership
        try:
            playlist = Playlist.objects.get(id=playlist_id, user=user)
        except Playlist.DoesNotExist:
            raise ValueError("Playlist not found or access denied")

        # 🔍 Validate track exists
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise ValueError("Track not found")

        # 🔢 Current size
        size = PlaylistItem.objects.filter(playlist=playlist).count()

        # 📍 Normalize position (1-based)
        if position is None or position > size + 1:
            position = size + 1

        if position < 1:
            raise ValueError("Position must be >= 1")

        # 🔄 Shift RIGHT safely in two phases to avoid unique constraint collisions
        PlaylistItem.objects.filter(
            playlist=playlist,
            position__gte=position
        ).update(position=models.F("position") + 1000)

        PlaylistItem.objects.filter(
            playlist=playlist,
            position__gte=position + 1000
        ).update(position=models.F("position") - 999)

        # ➕ Create item (FIXED: using track FK)
        item = PlaylistItem.objects.create(
            playlist=playlist,
            track=track,
            position=position
        )

        return item

    @staticmethod
    @transaction.atomic
    def remove_song_from_playlist(playlist_id, position, user):
        # 🔐 Validate playlist ownership
        try:
            playlist = Playlist.objects.get(id=playlist_id, user=user)
        except Playlist.DoesNotExist:
            raise ValueError("Playlist not found or access denied")

        # 🔍 Find item
        try:
            item = PlaylistItem.objects.get(
                playlist=playlist,
                position=position
            )
        except PlaylistItem.DoesNotExist:
            raise ValueError("Item not found at given position")

        removed_position = item.position

        # ❌ Delete
        item.delete()

        # 🔄 Shift LEFT
        PlaylistItem.objects.filter(
            playlist=playlist,
            position__gt=removed_position
        ).update(position=models.F("position") - 1)

    @staticmethod
    @transaction.atomic
    def reorder_playlist(playlist_id, new_order, user):
        # 🔐 Validate playlist ownership
        try:
            playlist = Playlist.objects.get(id=playlist_id, user=user)
        except Playlist.DoesNotExist:
            raise ValueError("Playlist not found or access denied")

        items = PlaylistItem.objects.filter(playlist=playlist)

        if not items.exists():
            raise ValueError("Playlist is empty")

        if len(new_order) != items.count():
            raise ValueError("Invalid reorder list length")

        item_map = {item.id: item for item in items}

        if set(new_order) != set(item_map.keys()):
            raise ValueError("Mismatch in playlist items")

        # 🚨 TEMP SHIFT (avoid unique constraint)
        PlaylistItem.objects.filter(playlist=playlist).update(
            position=models.F("position") + 1000
        )

        # ✅ Assign new positions (1-based)
        for index, item_id in enumerate(new_order, start=1):
            PlaylistItem.objects.filter(id=item_id).update(position=index)
    
    @staticmethod
    def get_playlist_length(playlist_id: int) -> int:
        return PlaylistItem.objects.filter(playlist_id=playlist_id).count()

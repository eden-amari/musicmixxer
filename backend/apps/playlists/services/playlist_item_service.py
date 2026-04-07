from django.db import transaction
from apps.playlists.models import Playlist, PlaylistItem
from django.db import models

class PlaylistItemService:

    @staticmethod
    @transaction.atomic
    def add_song_to_playlist(playlist_id, song_id, position=None):
        
        # Step 1: Validate playlist
        playlist = Playlist.objects.get(id=playlist_id)

        # Step 2: Get current size
        size = PlaylistItem.objects.filter(playlist=playlist).count()

        # Step 3: Normalize position
        if position is None or position > size:
            position = size

        if position < 0:
            raise ValueError("Position cannot be negative")

        # Step 4: Shift items (only if inserting not at end)
        items_to_shift = PlaylistItem.objects.filter(
            playlist=playlist,
            position__gte=position
        ).order_by('-position')

        for item in items_to_shift:
            item.position += 1
            item.save()
        # Step 5: Create new item
        item = PlaylistItem.objects.create(
            playlist=playlist,
            song_id=song_id,
            position=position
        )

        return item


    @staticmethod
    @transaction.atomic
    def remove_song_from_playlist(playlist_id, position):

        # Step 1: find item
        try:
            item = PlaylistItem.objects.get(
                playlist_id=playlist_id,
                position=position
            )
        except PlaylistItem.DoesNotExist:
            raise ValueError("Item not found at given position")

        removed_position = item.position

        # Step 2: delete item
        item.delete()

        # Step 3: shift LEFT (LOW → HIGH)
        items_to_shift = PlaylistItem.objects.filter(
            playlist_id=playlist_id,
            position__gt=removed_position
        ).order_by('position')

        for item in items_to_shift:
            item.position -= 1
            item.save()
    

    @staticmethod
    @transaction.atomic
    def reorder_playlist(playlist_id, new_order):

        # Step 1: fetch items
        items = PlaylistItem.objects.filter(playlist_id=playlist_id)

        if not items.exists():
            raise ValueError("Playlist is empty")

        if len(new_order) != items.count():
            raise ValueError("Invalid reorder list length")

        # Step 2: map item_id → item
        item_map = {item.id: item for item in items}

        # Step 3: validate IDs
        if set(new_order) != set(item_map.keys()):
            raise ValueError("Mismatch in playlist items")

        # Step 4: TEMP SHIFT (avoid unique constraint collision)
        for item in items:
            item.position += 1000
            item.save()

        # Step 5: assign new positions
        for index, item_id in enumerate(new_order):
            item = item_map[item_id]
            item.position = index
            item.save()
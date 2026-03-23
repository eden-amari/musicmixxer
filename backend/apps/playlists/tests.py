from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.playlists.models import Playlist, PlaylistItem
from apps.playlists.services.playlist_service import PlaylistService
from apps.playlists.services.playlist_item_service import PlaylistItemService


User = get_user_model()


class TestPlaylistService(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test123"
        )

    def test_create_playlist(self):
        playlist = PlaylistService.create_playlist(self.user, "Test")

        self.assertEqual(playlist.title, "Test")
        self.assertEqual(playlist.user, self.user)

    def test_create_playlist_empty_title(self):
        with self.assertRaises(ValueError):
            PlaylistService.create_playlist(self.user, "")

    def test_get_user_playlists(self):
        PlaylistService.create_playlist(self.user, "A")
        PlaylistService.create_playlist(self.user, "B")

        playlists = PlaylistService.get_user_playlists(self.user)

        self.assertEqual(playlists.count(), 2)

    def test_update_playlist(self):
        playlist = PlaylistService.create_playlist(self.user, "Old")

        updated = PlaylistService.update_playlist(
            playlist.id,
            self.user,
            {"title": "New"}
        )

        self.assertEqual(updated.title, "New")

    def test_update_playlist_not_owner(self):
        other_user = User.objects.create_user(
            username="otheruser",
            email="x@test.com",
            password="123"
        )

        playlist = PlaylistService.create_playlist(self.user, "Test")

        with self.assertRaises(PermissionError):
            PlaylistService.update_playlist(
                playlist.id,
                other_user,
                {"title": "Hack"}
            )

    def test_delete_playlist(self):
        playlist = PlaylistService.create_playlist(self.user, "Delete")

        PlaylistService.delete_playlist(playlist.id, self.user)

        self.assertEqual(Playlist.objects.count(), 0)

    def test_get_playlist_with_items(self):
        playlist = PlaylistService.create_playlist(self.user, "Test")

        PlaylistItemService.add_song_to_playlist(playlist.id, 1)
        PlaylistItemService.add_song_to_playlist(playlist.id, 2)

        data = PlaylistService.get_playlist_with_items(playlist.id, user=self.user)

        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["items"][0]["song_id"], 1)


class TestPlaylistItemService(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test123"
        )
        self.playlist = PlaylistService.create_playlist(self.user, "Test Playlist")

    # ----------------------
    # ADD TESTS
    # ----------------------

    def test_add_append(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 1)
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 2)

        items = PlaylistItem.objects.order_by('position')

        self.assertEqual(items[0].song_id, 1)
        self.assertEqual(items[1].song_id, 2)

    def test_add_insert_middle(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 1)
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 2)
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 3)

        PlaylistItemService.add_song_to_playlist(self.playlist.id, 99, position=1)

        items = list(PlaylistItem.objects.order_by('position'))

        self.assertEqual([i.song_id for i in items], [1, 99, 2, 3])

    def test_add_negative_position(self):
        with self.assertRaises(ValueError):
            PlaylistItemService.add_song_to_playlist(self.playlist.id, 1, position=-1)

    def test_add_position_out_of_bounds(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 1, position=100)

        item = PlaylistItem.objects.first()
        self.assertEqual(item.position, 0)

    def test_add_duplicates_allowed(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 1)
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 1)

        self.assertEqual(PlaylistItem.objects.count(), 2)

    # ----------------------
    # REMOVE TESTS
    # ----------------------

    def test_remove_middle(self):
        for i in [1, 2, 3, 4]:
            PlaylistItemService.add_song_to_playlist(self.playlist.id, i)

        PlaylistItemService.remove_song_from_playlist(self.playlist.id, 1)

        items = list(PlaylistItem.objects.order_by('position'))

        self.assertEqual([i.song_id for i in items], [1, 3, 4])

    def test_remove_first(self):
        for i in [1, 2, 3]:
            PlaylistItemService.add_song_to_playlist(self.playlist.id, i)

        PlaylistItemService.remove_song_from_playlist(self.playlist.id, 0)

        items = list(PlaylistItem.objects.order_by('position'))

        self.assertEqual([i.song_id for i in items], [2, 3])

    def test_remove_last(self):
        for i in [1, 2, 3]:
            PlaylistItemService.add_song_to_playlist(self.playlist.id, i)

        PlaylistItemService.remove_song_from_playlist(self.playlist.id, 2)

        items = list(PlaylistItem.objects.order_by('position'))

        self.assertEqual([i.song_id for i in items], [1, 2])

    def test_remove_invalid_position(self):
        with self.assertRaises(ValueError):
            PlaylistItemService.remove_song_from_playlist(self.playlist.id, 0)

    # ----------------------
    # REORDER TESTS
    # ----------------------

    def test_reorder_basic(self):
        items = []
        for i in [1, 2, 3]:
            item = PlaylistItemService.add_song_to_playlist(self.playlist.id, i)
            items.append(item)

        new_order = [items[2].id, items[0].id, items[1].id]

        PlaylistItemService.reorder_playlist(self.playlist.id, new_order)

        result = list(PlaylistItem.objects.order_by('position'))

        self.assertEqual([i.song_id for i in result], [3, 1, 2])

    def test_reorder_invalid_length(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 1)

        with self.assertRaises(ValueError):
            PlaylistItemService.reorder_playlist(self.playlist.id, [])

    def test_reorder_mismatch_items(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, 1)

        with self.assertRaises(ValueError):
            PlaylistItemService.reorder_playlist(self.playlist.id, [999])

    def test_reorder_with_duplicates(self):
        item1 = PlaylistItemService.add_song_to_playlist(self.playlist.id, 1)
        item2 = PlaylistItemService.add_song_to_playlist(self.playlist.id, 1)

        new_order = [item2.id, item1.id]

        PlaylistItemService.reorder_playlist(self.playlist.id, new_order)

        result = list(PlaylistItem.objects.order_by('position'))

        self.assertEqual([i.id for i in result], new_order)

    # ----------------------
    # INVARIANT TEST
    # ----------------------

    def test_positions_are_continuous(self):
        for i in [1, 2, 3, 4]:
            PlaylistItemService.add_song_to_playlist(self.playlist.id, i)

        PlaylistItemService.remove_song_from_playlist(self.playlist.id, 1)

        items = list(PlaylistItem.objects.order_by('position'))

        positions = [i.position for i in items]

        self.assertEqual(positions, list(range(len(items))))
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.playlists.models import Playlist, PlaylistItem
from apps.playlists.services.playlist_item_service import PlaylistItemService
from apps.playlists.services.playlist_service import PlaylistService
from apps.tracks.models import Track


User = get_user_model()


class TestPlaylistService(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test123",
        )
        self.track_one = Track.objects.create(
            title="Track One",
            artist="Artist One",
            unique_key="track-one-artist-one",
        )
        self.track_two = Track.objects.create(
            title="Track Two",
            artist="Artist Two",
            unique_key="track-two-artist-two",
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
            {"title": "New"},
        )

        self.assertEqual(updated.title, "New")

    def test_update_playlist_not_owner(self):
        other_user = User.objects.create_user(
            username="otheruser",
            email="x@test.com",
            password="123",
        )
        playlist = PlaylistService.create_playlist(self.user, "Test")

        with self.assertRaises(ValueError):
            PlaylistService.update_playlist(
                playlist.id,
                other_user,
                {"title": "Hack"},
            )

    def test_delete_playlist(self):
        playlist = PlaylistService.create_playlist(self.user, "Delete")

        PlaylistService.delete_playlist(playlist.id, self.user)

        self.assertEqual(Playlist.objects.count(), 0)

    def test_get_playlist_with_items(self):
        playlist = PlaylistService.create_playlist(self.user, "Test")
        PlaylistItemService.add_song_to_playlist(playlist.id, self.track_one.id, self.user)
        PlaylistItemService.add_song_to_playlist(playlist.id, self.track_two.id, self.user)

        data = PlaylistService.get_playlist_with_items(playlist.id, user=self.user)

        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["items"][0]["track"]["id"], self.track_one.id)
        self.assertEqual(data["items"][1]["track"]["id"], self.track_two.id)


class TestPlaylistItemService(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="test123",
        )
        self.playlist = PlaylistService.create_playlist(self.user, "Test Playlist")
        self.track_one = Track.objects.create(
            title="Track One",
            artist="Artist One",
            unique_key="track-one-artist-one",
        )
        self.track_two = Track.objects.create(
            title="Track Two",
            artist="Artist Two",
            unique_key="track-two-artist-two",
        )
        self.track_three = Track.objects.create(
            title="Track Three",
            artist="Artist Three",
            unique_key="track-three-artist-three",
        )
        self.track_four = Track.objects.create(
            title="Track Four",
            artist="Artist Four",
            unique_key="track-four-artist-four",
        )

    def test_add_append(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_one.id, self.user)
        PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_two.id, self.user)

        items = list(PlaylistItem.objects.order_by("position"))

        self.assertEqual(items[0].track_id, self.track_one.id)
        self.assertEqual(items[1].track_id, self.track_two.id)
        self.assertEqual([item.position for item in items], [1, 2])

    def test_add_insert_middle(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_one.id, self.user)
        PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_two.id, self.user)
        PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_three.id, self.user)
        PlaylistItemService.add_song_to_playlist(
            self.playlist.id,
            self.track_four.id,
            self.user,
            position=2,
        )

        items = list(PlaylistItem.objects.order_by("position"))

        self.assertEqual(
            [item.track_id for item in items],
            [self.track_one.id, self.track_four.id, self.track_two.id, self.track_three.id],
        )

    def test_add_negative_position(self):
        with self.assertRaises(ValueError):
            PlaylistItemService.add_song_to_playlist(
                self.playlist.id,
                self.track_one.id,
                self.user,
                position=-1,
            )

    def test_add_position_out_of_bounds_appends(self):
        item = PlaylistItemService.add_song_to_playlist(
            self.playlist.id,
            self.track_one.id,
            self.user,
            position=100,
        )

        self.assertEqual(item.position, 1)

    def test_add_duplicates_allowed(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_one.id, self.user)
        PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_one.id, self.user)

        self.assertEqual(PlaylistItem.objects.count(), 2)

    def test_remove_middle(self):
        for track in [self.track_one, self.track_two, self.track_three, self.track_four]:
            PlaylistItemService.add_song_to_playlist(self.playlist.id, track.id, self.user)

        PlaylistItemService.remove_song_from_playlist(self.playlist.id, 2, self.user)

        items = list(PlaylistItem.objects.order_by("position"))

        self.assertEqual([item.track_id for item in items], [self.track_one.id, self.track_three.id, self.track_four.id])
        self.assertEqual([item.position for item in items], [1, 2, 3])

    def test_remove_first(self):
        for track in [self.track_one, self.track_two, self.track_three]:
            PlaylistItemService.add_song_to_playlist(self.playlist.id, track.id, self.user)

        PlaylistItemService.remove_song_from_playlist(self.playlist.id, 1, self.user)

        items = list(PlaylistItem.objects.order_by("position"))

        self.assertEqual([item.track_id for item in items], [self.track_two.id, self.track_three.id])
        self.assertEqual([item.position for item in items], [1, 2])

    def test_remove_last(self):
        for track in [self.track_one, self.track_two, self.track_three]:
            PlaylistItemService.add_song_to_playlist(self.playlist.id, track.id, self.user)

        PlaylistItemService.remove_song_from_playlist(self.playlist.id, 3, self.user)

        items = list(PlaylistItem.objects.order_by("position"))

        self.assertEqual([item.track_id for item in items], [self.track_one.id, self.track_two.id])

    def test_remove_invalid_position(self):
        with self.assertRaises(ValueError):
            PlaylistItemService.remove_song_from_playlist(self.playlist.id, 1, self.user)

    def test_reorder_basic(self):
        items = []
        for track in [self.track_one, self.track_two, self.track_three]:
            item = PlaylistItemService.add_song_to_playlist(self.playlist.id, track.id, self.user)
            items.append(item)

        PlaylistItemService.reorder_playlist(
            self.playlist.id,
            [items[2].id, items[0].id, items[1].id],
            self.user,
        )

        result = list(PlaylistItem.objects.order_by("position"))

        self.assertEqual([item.track_id for item in result], [self.track_three.id, self.track_one.id, self.track_two.id])

    def test_reorder_invalid_length(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_one.id, self.user)

        with self.assertRaises(ValueError):
            PlaylistItemService.reorder_playlist(self.playlist.id, [], self.user)

    def test_reorder_mismatch_items(self):
        PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_one.id, self.user)

        with self.assertRaises(ValueError):
            PlaylistItemService.reorder_playlist(self.playlist.id, [999], self.user)

    def test_reorder_with_duplicates(self):
        item_one = PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_one.id, self.user)
        item_two = PlaylistItemService.add_song_to_playlist(self.playlist.id, self.track_one.id, self.user)

        new_order = [item_two.id, item_one.id]
        PlaylistItemService.reorder_playlist(self.playlist.id, new_order, self.user)

        result = list(PlaylistItem.objects.order_by("position"))

        self.assertEqual([item.id for item in result], new_order)

    def test_positions_are_continuous(self):
        for track in [self.track_one, self.track_two, self.track_three, self.track_four]:
            PlaylistItemService.add_song_to_playlist(self.playlist.id, track.id, self.user)

        PlaylistItemService.remove_song_from_playlist(self.playlist.id, 2, self.user)

        items = list(PlaylistItem.objects.order_by("position"))

        self.assertEqual([item.position for item in items], [1, 2, 3])

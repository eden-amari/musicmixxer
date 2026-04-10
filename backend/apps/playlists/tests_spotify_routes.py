from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.playlists.models import Playlist


User = get_user_model()


class SpotifyPlaylistRouteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="spotifyroutes",
            email="spotifyroutes@example.com",
            password="testpass123",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.client.defaults["HTTP_X_SPOTIFY_ACCESS_TOKEN"] = "spotify-token"

    @patch("apps.playlists.api.routes.SpotifyClient")
    def test_get_spotify_playlist_tracks_supports_track_payloads(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.get_playlist_items.return_value = [
            {
                "track": {
                    "name": "Song A",
                    "id": "spotify-track-a",
                    "artists": [{"name": "Artist A"}],
                    "album": {
                        "name": "Album A",
                        "images": [{"url": "https://example.com/a.jpg"}],
                    },
                }
            }
        ]

        response = self.client.get("/api/playlists/spotify/playlists/playlist-123")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(len(payload["data"]), 1)
        self.assertEqual(payload["data"][0]["spotify_id"], "spotify-track-a")
        self.assertEqual(payload["data"][0]["artist"], "Artist A")

    @patch("apps.playlists.api.routes.SpotifyClient")
    def test_get_spotify_playlist_tracks_supports_item_payloads(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.get_playlist_items.return_value = [
            {
                "item": {
                    "name": "Song B",
                    "id": "spotify-track-b",
                    "artists": [{"name": "Artist B"}],
                    "album": {
                        "name": "Album B",
                        "images": [{"url": "https://example.com/b.jpg"}],
                    },
                }
            }
        ]

        response = self.client.get("/api/playlists/spotify/playlists/playlist-456")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"][0]["spotify_id"], "spotify-track-b")


class PlaylistApiStatusTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="playliststatus",
            email="playliststatus@example.com",
            password="testpass123",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_missing_playlist_returns_404(self):
        response = self.client.get("/api/playlists/999999")
        payload = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(payload["success"])

    def test_create_playlist_with_empty_title_returns_400(self):
        response = self.client.post(
            "/api/playlists/",
            {"title": "", "description": ""},
            format="json",
        )
        payload = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(payload["success"])

    def test_export_playlist_without_spotify_token_returns_400(self):
        playlist = Playlist.objects.create(user=self.user, title="Needs Token")

        response = self.client.post(
            f"/api/playlists/{playlist.id}/export",
            {"name": "Export Me"},
            format="json",
        )
        payload = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(payload["success"])

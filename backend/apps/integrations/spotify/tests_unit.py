from unittest.mock import patch

from django.test import SimpleTestCase

from apps.integrations.spotify.client import SpotifyClient


class SpotifyClientTests(SimpleTestCase):
    @patch.object(SpotifyClient, "_request")
    @patch.object(SpotifyClient, "get_current_user")
    def test_create_playlist_uses_current_user_endpoint(self, mock_get_current_user, mock_request):
        mock_get_current_user.return_value = {"id": "spotify-user-123"}
        mock_request.return_value = {"id": "playlist-123"}

        client = SpotifyClient("token")
        result = client.create_playlist(
            name="My Playlist",
            description="Created in test",
            public=False,
        )

        mock_request.assert_called_once_with(
            "POST",
            "/users/spotify-user-123/playlists",
            json={
                "name": "My Playlist",
                "description": "Created in test",
                "public": False,
            },
        )
        self.assertEqual(result["id"], "playlist-123")

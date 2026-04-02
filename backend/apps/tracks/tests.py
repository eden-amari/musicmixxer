from django.test import TestCase
from unittest.mock import patch

from apps.tracks.services.resolver import TrackResolver
from apps.tracks.services.enrichment_service import EnrichmentService
from apps.tracks.services.track_services import TrackService
from apps.tracks.models import Track


class TrackPipelineTest(TestCase):

    def setUp(self):
        self.sample_input = {
            "title": "blinding lights",
            "artist": None,
            "bpm": None,
            "genre": None,
            "energy": None,
            "external_id": None
        }

        self.mock_spotify_response = {
            "tracks": {
                "items": [
                    {
                        "name": "Blinding Lights",
                        "id": "mock_id_123",
                        "artists": [{"name": "The Weeknd"}]
                    }
                ]
            }
        }

    @patch("apps.integrations.spotify.client.SpotifyClient.search_tracks")
    def test_resolver(self, mock_search):

        mock_search.return_value = self.mock_spotify_response

        result = TrackResolver.resolve(self.sample_input, access_token="dummy")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Blinding Lights")
        self.assertEqual(result["artist"], "The Weeknd")
        self.assertEqual(result["external_id"], "mock_id_123")

    @patch("apps.integrations.spotify.client.SpotifyClient.search_tracks")
    def test_enrichment(self, mock_search):

        mock_search.return_value = self.mock_spotify_response

        result = EnrichmentService.enrich(self.sample_input, access_token="dummy")

        self.assertEqual(result["title"], "Blinding Lights")
        self.assertEqual(result["artist"], "The Weeknd")
        self.assertEqual(result["external_id"], "mock_id_123")

    @patch("apps.integrations.spotify.client.SpotifyClient.search_tracks")
    def test_full_pipeline_save(self, mock_search):

        mock_search.return_value = self.mock_spotify_response

        enriched = EnrichmentService.enrich(self.sample_input, access_token="dummy")

        track = TrackService.create_safe(enriched)

        self.assertIsNotNone(track.id)
        self.assertEqual(track.title, "Blinding Lights")
        self.assertEqual(track.artist, "The Weeknd")
        self.assertEqual(track.external_id, "mock_id_123")

        self.assertEqual(Track.objects.count(), 1)

    def test_invalid_input(self):

        data = {
            "title": None
        }

        result = EnrichmentService.enrich(data, access_token="dummy")

        self.assertEqual(result, data)
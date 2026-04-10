from django.test import TestCase

from apps.imports.domain.normalizer import Normalizer


class NormalizerTests(TestCase):
    def test_normalize_preserves_spotify_id(self):
        normalized = Normalizer.normalize(
            {
                "title": "Song",
                "artist": "Artist",
                "spotify_id": "spotify-123",
            }
        )

        self.assertEqual(normalized["spotify_id"], "spotify-123")

    def test_normalize_supports_legacy_external_id(self):
        normalized = Normalizer.normalize(
            {
                "title": "Song",
                "artist": "Artist",
                "external_id": "spotify-legacy",
            }
        )

        self.assertEqual(normalized["spotify_id"], "spotify-legacy")

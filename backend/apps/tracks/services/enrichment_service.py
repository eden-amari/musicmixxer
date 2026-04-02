from typing import Dict

from apps.tracks.services.feature_service import AudioFeatureService


class EnrichmentService:

    _cache = {}
    _daily_limit = 100
    _calls_made = 0

    @classmethod
    def enrich(cls, data: Dict, access_token: str) -> Dict:

        spotify_id = data.get("spotify_id")

        # ------------------------
        # SKIP INVALID
        # ------------------------
        if not spotify_id:
            return data

        # ------------------------
        # CACHE FIRST
        # ------------------------
        if spotify_id in cls._cache:
            return cls._cache[spotify_id]

        # ------------------------
        # SKIP IF ALREADY ENRICHED
        # ------------------------
        if data.get("bpm") and data.get("energy"):
            return data

        # ------------------------
        # RATE LIMIT
        # ------------------------
        if cls._calls_made >= cls._daily_limit:
            return data

        try:
            enriched = cls._enrich_internal(data)

            if enriched != data:
                cls._calls_made += 1

            cls._cache[spotify_id] = enriched

            return enriched

        except Exception:
            return data

    @classmethod
    def _enrich_internal(cls, data: Dict) -> Dict:

        spotify_id = data.get("spotify_id")

        if not spotify_id:
            return data

        features = AudioFeatureService.get_features(
            spotify_id,
            title=data.get("title"),
            artist=data.get("artist")
        )

        if not features:
            return data

        return {
            **data,
            "bpm": features.get("bpm") or data.get("bpm"),
            "energy": features.get("energy") or data.get("energy"),
            "valence": features.get("valence") or data.get("valence"),
            "danceability": features.get("danceability") or data.get("danceability"),
            "loudness": features.get("loudness") or data.get("loudness"),
        }
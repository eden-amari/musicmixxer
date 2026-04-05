from typing import Dict
import time

from apps.tracks.services.feature_service import AudioFeatureService


class EnrichmentService:

    _cache = {}
    _daily_limit = 100
    _calls_made = 0
    _last_call_time = 0

    _rate_limit_per_sec = 1
    _retry_attempts = 2

    @classmethod
    def enrich(cls, data: Dict, access_token: str) -> Dict:

        spotify_id = data.get("spotify_id")

        if not spotify_id:
            return data

        if spotify_id in cls._cache:
            return cls._cache[spotify_id]

        if data.get("bpm") and data.get("energy"):
            return data

        if cls._calls_made >= cls._daily_limit:
            return data

        enriched = cls._safe_enrich(data)

        cls._cache[spotify_id] = enriched

        return enriched

    @classmethod
    def _safe_enrich(cls, data: Dict) -> Dict:

        for attempt in range(cls._retry_attempts):

            cls._throttle()

            try:
                enriched = cls._enrich_internal(data)

                if enriched != data:
                    cls._calls_made += 1

                return enriched

            except Exception as e:
                error_str = str(e)

                print(f"[Enrichment Error] attempt={attempt} error={error_str}")

                if "429" in error_str:
                    time.sleep(2)
                    continue

                if "timeout" in error_str.lower():
                    time.sleep(1)
                    continue

                return data

        return data

    @classmethod
    def _throttle(cls):
        now = time.time()
        elapsed = now - cls._last_call_time

        if elapsed < 1:
            time.sleep(1 - elapsed)

        cls._last_call_time = time.time()

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
from typing import Dict
import time
import logging

from apps.tracks.services.feature_service import AudioFeatureService


logger = logging.getLogger(__name__)


class EnrichmentService:

    _cache = {}
    _daily_limit = 100
    _calls_made = 0
    _last_call_time = 0

    _rate_limit_per_sec = 0.3   # ✅ ~1 request every 3 seconds
    _retry_attempts = 3         # ✅ slightly more retries

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
                logger.warning(
                    "Track enrichment attempt %s failed for spotify_id=%s: %s",
                    attempt + 1,
                    data.get("spotify_id"),
                    error_str,
                )

                # 🔥 SMART BACKOFF
                if "429" in error_str:
                    time.sleep(3 + attempt * 2)   # 3s → 5s → 7s
                    continue

                if "timeout" in error_str.lower():
                    time.sleep(2 + attempt)       # 2s → 3s → 4s
                    continue

                return data

        return data

    @classmethod
    def _throttle(cls):
        now = time.time()

        # minimum interval between calls
        min_interval = 1 / cls._rate_limit_per_sec   # ~3.33 sec

        elapsed = now - cls._last_call_time

        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

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

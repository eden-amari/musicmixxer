import requests
from typing import Dict, Optional
from django.conf import settings

class AudioFeatureService:
    """
    Fetch audio features using SoundNet (RapidAPI Track Analysis API).

    Strategy:
    - PRIMARY: Spotify track ID
    - FALLBACK: title + artist
    - Fail gracefully
    """

    BASE_URL = "https://track-analysis.p.rapidapi.com"
    HEADERS = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "track-analysis.p.rapidapi.com"
    }

    TIMEOUT = 5

    # ==================================================
    # PUBLIC ENTRY
    # ==================================================

    @classmethod
    def get_features(
        cls,
        external_id: str,
        title: str = None,
        artist: str = None
    ) -> Optional[Dict]:

        # ------------------------
        # PRIMARY: Spotify ID
        # ------------------------
        if external_id:
            features = cls._fetch_by_spotify_id(external_id)
            if features:
                return features

        # ------------------------
        # FALLBACK: title search
        # ------------------------
        if title:
            return cls._fetch_by_query(title, artist)

        return None

    # ==================================================
    # FETCH METHODS
    # ==================================================

    @classmethod
    def _fetch_by_spotify_id(cls, external_id: str) -> Optional[Dict]:
        url = f"{cls.BASE_URL}/pktx/spotify/{external_id}"

        try:
            response = requests.get(
                url,
                headers=cls.HEADERS,
                timeout=cls.TIMEOUT
            )

            if response.status_code != 200:
                print("Audio API error:", response.status_code, response.text)
                return None

            return cls._normalize_response(response.json())

        except Exception as e:
            print("Audio API exception:", str(e))
            return None

    @classmethod
    def _fetch_by_query(cls, title: str, artist: str = None) -> Optional[Dict]:
        url = f"{cls.BASE_URL}/pktx/analysis"

        params = {"song": title}
        if artist:
            params["artist"] = artist

        try:
            response = requests.get(
                url,
                headers=cls.HEADERS,
                params=params,
                timeout=cls.TIMEOUT
            )

            if response.status_code != 200:
                print("Audio API fallback error:", response.status_code, response.text)
                return None

            return cls._normalize_response(response.json())

        except Exception as e:
            print("Audio API fallback exception:", str(e))
            return None

    # ==================================================
    # NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_response(data: Dict) -> Dict:
        """
        Normalize API response → internal format

        Returns:
        {
            bpm: int
            energy: float (0–1)
            danceability: float (0–1)
            loudness: float
            valence: float (optional mood)
        }
        """

        return {
            "bpm": AudioFeatureService._safe_int(data.get("tempo")),
            "energy": AudioFeatureService._normalize_percent(data.get("energy")),
            "danceability": AudioFeatureService._normalize_percent(data.get("danceability")),
            "loudness": AudioFeatureService._safe_float(data.get("loudness")),
            "valence": AudioFeatureService._normalize_percent(
                data.get("happiness")  # maps to mood
            ),
        }

    # ==================================================
    # HELPERS
    # ==================================================

    @staticmethod
    def _safe_int(value):
        try:
            return int(value) if value is not None else None
        except:
            return None

    @staticmethod
    def _safe_float(value):
        try:
            if value is None:
                return None

            # handle "-5 dB"
            if isinstance(value, str):
                value = value.replace(" dB", "")

            return float(value)

        except:
            return None

    @staticmethod
    def _normalize_percent(value):
        """
        Normalize 0–100 → 0–1
        OR pass through if already 0–1
        """
        try:
            if value is None:
                return None

            value = float(value)

            if value > 1:
                return value / 100

            return value

        except:
            return None
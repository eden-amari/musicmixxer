import re
from typing import Generator, Dict, Tuple, Optional


class SpotifyParser:

    MAX_ITEMS = 50000

    @staticmethod
    def parse(response) -> Generator[Tuple[Optional[Dict], Optional[str]], None, None]:

        items = SpotifyParser._extract_items(response)

        for idx, item in enumerate(items):
            if idx >= SpotifyParser.MAX_ITEMS:
                yield None, f"Item limit exceeded ({SpotifyParser.MAX_ITEMS})"
                break

            try:
                track = SpotifyParser._extract_track(item)

                if not track:
                    continue

                normalized = SpotifyParser._normalize_track(track)

                yield normalized, None

            except Exception as e:
                yield None, f"Item {idx}: {str(e)}"

    @staticmethod
    def _extract_items(response):

        if isinstance(response, list):
            return response

        if not isinstance(response, dict):
            raise ValueError("Invalid Spotify response")

        if "items" in response:
            return response["items"]

        if "tracks" in response and "items" in response["tracks"]:
            return response["tracks"]["items"]

        return []

    @staticmethod
    def _extract_track(item):

        if not isinstance(item, dict):
            return None

        track = item.get("track") or item.get("item")

        if not track:
            return None

        if track.get("is_local"):
            return None

        if track.get("type") != "track":
            return None

        return track

    @staticmethod
    def _normalize_track(track):

        title = SpotifyParser._clean_text(track.get("name"))
        artist = SpotifyParser._extract_artist(track)
        spotify_id = track.get("id")

        if not title:
            raise ValueError("Missing title")

        if not spotify_id:
            raise ValueError("Missing Spotify ID")

        return {
            "title": title,
            "artist": artist,
            "bpm": None,
            "genre": None,
            "energy": None,
            "spotify_id": spotify_id,  # ✅ FIXED
        }

    @staticmethod
    def _extract_artist(track):

        artists = track.get("artists")

        if isinstance(artists, list) and artists:
            return SpotifyParser._clean_text(artists[0].get("name"))

        return None

    @staticmethod
    def _clean_text(value):

        if not value:
            return None

        value = str(value).strip()
        value = re.sub(r"[^\w\s\-\.\,\&\(\)]", "", value)
        value = re.sub(r"\s+", " ", value)

        return value
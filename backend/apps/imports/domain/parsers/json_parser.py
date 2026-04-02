import json
import re
from io import StringIO
from typing import Generator, Dict, Tuple, Optional


class JSONParser:
    """
    Production-grade JSON parser for ingestion.

    Responsibilities:
    - Safe JSON decoding with encoding fallback
    - Normalize root structure into iterable list
    - Handle nested and inconsistent schemas
    - Clean and normalize values using regex
    - Isolate errors per item
    """

    HEADER_MAP = {
        "title": ["title", "name", "track", "track_name", "song"],
        "artist": ["artist", "artist_name", "singer"],
        "bpm": ["bpm", "tempo"],
        "genre": ["genre", "category"],
        "energy": ["energy", "intensity"],
        "spotify_id": ["external_id", "id", "spotify_id"],
    }

    NULL_VALUES = {"", " ", "null", "none", "n/a", "-", "--"}

    MAX_ITEMS = 50000

    @staticmethod
    def parse(file) -> Generator[Tuple[Optional[Dict], Optional[str]], None, None]:
        """
        Parse JSON file and yield normalized rows.

        Yields:
            (data_dict, error_message)
        """
        data = JSONParser._load_json(file)

        items = JSONParser._normalize_root(data)

        for idx, item in enumerate(items):
            if idx >= JSONParser.MAX_ITEMS:
                yield None, f"Item limit exceeded ({JSONParser.MAX_ITEMS})"
                break

            try:
                flattened = JSONParser._extract_structure(item)
                normalized = JSONParser._normalize_row(flattened)
                yield normalized, None

            except Exception as e:
                yield None, f"Item {idx}: {str(e)}"

    @staticmethod
    def _load_json(file):
        """
        Load JSON with encoding fallback.
        """
        try:
            content = file.read()
            file.seek(0)

            try:
                decoded = content.decode("utf-8")
            except Exception:
                decoded = content.decode("latin-1", errors="ignore")

            return json.loads(decoded)

        except Exception:
            raise ValueError("Invalid JSON file")

    @staticmethod
    def _normalize_root(data):
        """
        Normalize root JSON structure into list.
        """
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in ["tracks", "items", "data"]:
                if key in data and isinstance(data[key], list):
                    return data[key]

        return [data]

    @staticmethod
    def _extract_structure(item):
        """
        Flatten nested structures.
        """
        if not isinstance(item, dict):
            raise ValueError("Invalid item structure")

        if "track" in item and isinstance(item["track"], dict):
            track = item["track"]

            return {
                "title": track.get("name"),
                "artist": JSONParser._extract_artist(track),
                "spotify_id": track.get("id"),
            }

        return item

    @staticmethod
    def _extract_artist(track):
        """
        Extract artist from nested structure.
        """
        artists = track.get("artists")

        if isinstance(artists, list) and artists:
            return artists[0].get("name")

        return track.get("artist")

    @staticmethod
    def _normalize_row(row):
        """
        Normalize row into Track schema.
        """
        data = {
            "title": None,
            "artist": None,
            "bpm": None,
            "genre": None,
            "energy": None,
            "spotify_id": None,
        }

        for key, value in row.items():
            clean_key = JSONParser._normalize_text(key)

            for target, aliases in JSONParser.HEADER_MAP.items():
                for alias in aliases:
                    if re.fullmatch(alias, clean_key):
                        cleaned_value = JSONParser._clean_value(value)

                        if target == "bpm":
                            data["bpm"] = JSONParser._parse_int(cleaned_value)
                        elif target == "energy":
                            data["energy"] = JSONParser._parse_float(cleaned_value)
                        else:
                            data[target] = cleaned_value

        if not data["title"]:
            raise ValueError("Missing title")

        return data

    @staticmethod
    def _clean_value(value):
        """
        Clean value using regex normalization.
        """
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if value.lower() in JSONParser.NULL_VALUES:
                return None

            value = re.sub(r"[^\w\s\-\.\,\&\(\)]", "", value)
            value = re.sub(r"\s+", " ", value)

        return value

    @staticmethod
    def _parse_int(value):
        """
        Safe integer parsing.
        """
        try:
            return int(float(value))
        except Exception:
            return None

    @staticmethod
    def _parse_float(value):
        """
        Safe float parsing.
        """
        try:
            return float(value)
        except Exception:
            return None

    @staticmethod
    def _normalize_text(text):
        """
        Normalize keys for matching.
        """
        text = str(text).lower().strip()
        text = re.sub(r"[\s\-]+", "_", text)
        text = re.sub(r"[^\w_]", "", text)
        return text
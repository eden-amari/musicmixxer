import csv
import re
from io import StringIO
from typing import Generator, Dict, Tuple, Optional


class CSVParser:
    """
    Production-grade CSV parser for streaming ingestion.

    Responsibilities:
    - Detect encoding and decode safely
    - Detect delimiter dynamically
    - Normalize and map headers using regex
    - Clean and normalize row values
    - Handle malformed rows without breaking pipeline
    - Stream rows to avoid memory overhead

    Output:
    Yields (data_dict, error_message)
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

    MAX_ROWS = 50000

    @staticmethod
    def parse(file) -> Generator[Tuple[Optional[Dict], Optional[str]], None, None]:
        """
        Parse CSV file as a generator.

        Args:
            file: Uploaded file object

        Yields:
            Tuple[Dict or None, error message or None]
        """
        decoded_file = CSVParser._decode_file(file)

        try:
            sample = decoded_file.read(2048)
            decoded_file.seek(0)
            dialect = csv.Sniffer().sniff(sample)
        except Exception:
            dialect = csv.excel

        reader = csv.DictReader(decoded_file, dialect=dialect)

        if not reader.fieldnames:
            yield None, "Missing headers"
            return

        header_map = CSVParser._normalize_headers(reader.fieldnames)

        if "title" not in header_map.values():
            yield None, "Missing required column: title"
            return

        for idx, raw_row in enumerate(reader):
            if idx >= CSVParser.MAX_ROWS:
                yield None, f"Row limit exceeded ({CSVParser.MAX_ROWS})"
                break

            try:
                cleaned = CSVParser._clean_row(raw_row, header_map)
                yield cleaned, None
            except Exception as e:
                yield None, f"Row {idx}: {str(e)}"

    @staticmethod
    def _decode_file(file):
        """
        Decode file content with fallback encoding.

        Returns:
            StringIO object
        """
        try:
            content = file.read()
            file.seek(0)

            try:
                decoded = content.decode("utf-8")
            except Exception:
                decoded = content.decode("latin-1", errors="ignore")

            return StringIO(decoded)
        except Exception:
            raise ValueError("Invalid file encoding")

    @staticmethod
    def _normalize_headers(headers):
        """
        Normalize headers and map them to internal schema keys.

        Args:
            headers (list[str])

        Returns:
            dict mapping original header -> normalized key
        """
        normalized = {}

        for header in headers:
            clean = CSVParser._normalize_text(header)

            for target, aliases in CSVParser.HEADER_MAP.items():
                for alias in aliases:
                    if re.fullmatch(alias, clean):
                        normalized[header] = target

        return normalized

    @staticmethod
    def _clean_row(row, header_map):
        """
        Clean and normalize a single row.

        Args:
            row (dict)
            header_map (dict)

        Returns:
            dict
        """
        data = {
            "title": None,
            "artist": None,
            "bpm": None,
            "genre": None,
            "energy": None,
            "spotify_id": None,
        }

        for original_key, value in row.items():
            if original_key not in header_map:
                continue

            key = header_map[original_key]
            cleaned_value = CSVParser._clean_value(value)

            if key == "bpm":
                data["bpm"] = CSVParser._parse_int(cleaned_value)
            elif key == "energy":
                data["energy"] = CSVParser._parse_float(cleaned_value)
            else:
                data[key] = cleaned_value

        if not data["title"]:
            raise ValueError("Missing title")

        return data

    @staticmethod
    def _clean_value(value):
        """
        Normalize raw value using regex cleaning.

        Args:
            value (str)

        Returns:
            str or None
        """
        if value is None:
            return None

        value = value.strip()

        if value.lower() in CSVParser.NULL_VALUES:
            return None

        value = re.sub(r"[^\w\s\-\.\,\&\(\)]", "", value)
        value = re.sub(r"\s+", " ", value)

        return value

    @staticmethod
    def _parse_int(value):
        """
        Safely parse integer values.

        Args:
            value (str)

        Returns:
            int or None
        """
        if value is None:
            return None
        try:
            return int(float(value))
        except Exception:
            return None

    @staticmethod
    def _parse_float(value):
        """
        Safely parse float values.

        Args:
            value (str)

        Returns:
            float or None
        """
        if value is None:
            return None
        try:
            return float(value)
        except Exception:
            return None

    @staticmethod
    def _normalize_text(text):
        """
        Normalize header text for matching.

        Args:
            text (str)

        Returns:
            str
        """
        text = text.lower().strip()
        text = re.sub(r"[\s\-]+", "_", text)
        text = re.sub(r"[^\w_]", "", text)
        return text
# apps/imports/domain/normalizer.py

class Normalizer:
    """
    Responsible for transforming parsed track data into a clean,
    consistent structure for downstream processing.

    Assumes input is already semi-structured (e.g., from SpotifyParser).

    Responsibilities:
    - Clean string fields
    - Coerce numeric types
    - Apply defaults
    - Ensure consistent schema

    Output schema:
    {
        "title": str,
        "artist": str,
        "bpm": int | None,
        "genre": str,
        "energy": float | None,
        "external_id": str
    }
    """

    @staticmethod
    def normalize(row: dict) -> dict:
        """
        Normalize a track dictionary into standard schema.

        Args:
            row (dict): Parsed track data

        Returns:
            dict: Clean normalized track
        """

        return {
            "title": Normalizer._clean_str(row.get("title")),
            "artist": Normalizer._clean_str(row.get("artist")),
            "bpm": Normalizer._safe_int(row.get("bpm")),
            "genre": Normalizer._clean_str(row.get("genre")) or "unknown",
            "energy": Normalizer._safe_float(row.get("energy")),
            "spotify_id": Normalizer._clean_str(row.get("external_id")),
        }

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    @staticmethod
    def _clean_str(value):
        """
        Normalize string values.

        - Cast to string
        - Strip whitespace
        - Return None if empty

        Args:
            value (Any)

        Returns:
            str | None
        """
        if value is None:
            return None

        value = str(value).strip()

        return value if value else None

    @staticmethod
    def _safe_int(value):
        """
        Safely convert to int.

        Returns None if invalid.

        Args:
            value (Any)

        Returns:
            int | None
        """
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_float(value):
        """
        Safely convert to float.

        Returns None if invalid.

        Args:
            value (Any)

        Returns:
            float | None
        """
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
# apps/imports/domain/validator.py

def validate_track(track: dict) -> str | None:
    """
    Validate normalized track data.

    Returns:
        None if valid
        str error message if invalid

    Validation Rules:
    - title is required
    - bpm must be between 1 and 300 if present
    - energy must be between 0 and 1 if present

    Notes:
    - spotify_id is OPTIONAL (can be resolved/enriched later)
    """

    # ------------------------
    # REQUIRED FIELDS
    # ------------------------
    if not track.get("title"):
        return "Missing title"

    # Optional (recommended but not required)
    # if not track.get("artist"):
    #     return "Missing artist"

    # ------------------------
    # OPTIONAL FIELD VALIDATION
    # ------------------------

    bpm = track.get("bpm")
    if bpm is not None:
        if bpm <= 0 or bpm > 300:
            return "Invalid bpm (must be between 1 and 300)"

    energy = track.get("energy")
    if energy is not None:
        if energy < 0 or energy > 1:
            return "Invalid energy (must be between 0 and 1)"

    return None